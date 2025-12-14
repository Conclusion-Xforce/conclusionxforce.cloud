"""
Lambda function to start Bitwarden ECS container
Handles:
- Starting ECS Fargate task in private subnet
- Updating Route53 DNS record to point to API Gateway custom domain
- Triggering Step Functions for auto-shutdown

Runtime: Python 3.13
"""

import json
import os
import time
import boto3
from typing import Dict, Any

# AWS clients
ecs = boto3.client('ecs')
route53 = boto3.client('route53')
stepfunctions = boto3.client('stepfunctions')

# Environment variables from CDK
CLUSTER_NAME = os.environ['CLUSTER_NAME']
TASK_DEFINITION = os.environ['TASK_DEFINITION']
SUBNET_IDS = os.environ['SUBNET_IDS'].split(',')
CONTAINER_SECURITY_GROUP_ID = os.environ['CONTAINER_SECURITY_GROUP_ID']
CONTAINER_NAME = os.environ['CONTAINER_NAME']
STATE_MACHINE_ARN = os.environ['STATE_MACHINE_ARN']

# API Gateway and Route53 configuration (required)
API_GATEWAY_DOMAIN_NAME = os.environ['API_GATEWAY_DOMAIN_NAME']  # e.g., d-abc123.execute-api.us-east-1.amazonaws.com
API_GATEWAY_HOSTED_ZONE_ID = os.environ['API_GATEWAY_HOSTED_ZONE_ID']  # API Gateway's Route53 zone ID
HOSTED_ZONE_ID = os.environ['HOSTED_ZONE_ID']
FQDN = os.environ['FQDN']


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler
    
    Expected event:
    {
        "sourceIp": "203.0.113.42"  # Optional - for logging
    }
    """
    try:
        source_ip = event.get('sourceIp', 'unknown')
        print(f"Starting Bitwarden container (requested by: {source_ip})")
        
        # Step 1: Start ECS task
        task_arn = start_ecs_task()
        
        # Step 2: Update DNS to point to API Gateway (Alias record)
        update_dns_record()
        
        # Step 3: Start Step Functions workflow for auto-shutdown
        execution_arn = start_shutdown_workflow(task_arn)
        
        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Bitwarden container started successfully',
                'url': f'https://{FQDN}',
                'taskArn': task_arn,
                'executionArn': execution_arn,
                'autoShutdownMinutes': int(os.environ.get('AUTO_SHUTDOWN_MINUTES', '30'))
            })
        }
        
    except Exception as e:
        print(f"Error starting container: {str(e)}")
        return error_response(500, f"Failed to start container: {str(e)}")


def start_ecs_task() -> str:
    """
    Start ECS Fargate task in private subnet
    
    Returns:
        str: task_arn
    """
    print(f"Starting ECS task in cluster {CLUSTER_NAME}")
    
    # Start the task
    response = ecs.run_task(
        cluster=CLUSTER_NAME,
        taskDefinition=TASK_DEFINITION,
        launchType='FARGATE',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': SUBNET_IDS,
                'securityGroups': [CONTAINER_SECURITY_GROUP_ID],
                'assignPublicIp': 'DISABLED'  # Private subnet, no public IP needed
            }
        },
        count=1
    )
    
    if not response['tasks']:
        raise Exception("Failed to start ECS task")
    
    task_arn = response['tasks'][0]['taskArn']
    print(f"Task started: {task_arn}")
    
    # Wait for task to be running and healthy
    wait_for_task_healthy(task_arn)
    
    return task_arn


def wait_for_task_healthy(task_arn: str, max_attempts: int = 60) -> None:
    """
    Wait for ECS task to be running and registered with ECS Service
    
    Args:
        task_arn: ECS task ARN
        max_attempts: Maximum number of attempts (2 seconds each = 2 minutes)
    """
    print("Waiting for task to be healthy...")
    
    for attempt in range(max_attempts):
        response = ecs.describe_tasks(
            cluster=CLUSTER_NAME,
            tasks=[task_arn]
        )
        
        if not response['tasks']:
            raise Exception("Task not found")
        
        task = response['tasks'][0]
        last_status = task['lastStatus']
        
        print(f"Task status: {last_status} (attempt {attempt + 1}/{max_attempts})")
        
        # Check if task has failed
        if last_status == 'STOPPED':
            raise Exception(f"Task stopped unexpectedly: {task.get('stoppedReason', 'Unknown')}")
        
        # Check if task is running
        if last_status == 'RUNNING':
            # Give VPC Link a few more seconds to register the target
            time.sleep(10)
            print("Task is running and should be accessible via API Gateway")
            return
        
        # Wait before next attempt
        time.sleep(2)
    
    raise Exception("Timeout waiting for task to be healthy")


def update_dns_record() -> None:
    """
    Update Route53 Alias record to point to API Gateway custom domain
    Uses Alias record (not A record) for better integration with API Gateway
    """
    print(f"Updating DNS record {FQDN} -> API Gateway")
    
    try:
        route53.change_resource_record_sets(
            HostedZoneId=HOSTED_ZONE_ID,
            ChangeBatch={
                'Changes': [{
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': FQDN,
                        'Type': 'A',
                        'AliasTarget': {
                            'HostedZoneId': API_GATEWAY_HOSTED_ZONE_ID,  # API Gateway's canonical zone ID
                            'DNSName': API_GATEWAY_DOMAIN_NAME,
                            'EvaluateTargetHealth': False
                        }
                    }
                }]
            }
        )
        print(f"DNS Alias record created successfully")
    except Exception as e:
        print(f"Warning: Failed to update DNS record: {str(e)}")
        # Don't fail the entire operation if DNS update fails


def start_shutdown_workflow(task_arn: str) -> str:
    """
    Start Step Functions workflow for auto-shutdown
    
    Args:
        task_arn: ECS task ARN to monitor
    
    Returns:
        str: Step Functions execution ARN
    """
    print("Starting auto-shutdown workflow")
    
    response = stepfunctions.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        input=json.dumps({
            'taskArn': task_arn,
            'clusterName': CLUSTER_NAME,
            'hostedZoneId': HOSTED_ZONE_ID,
            'fqdn': FQDN,
            'apiGatewayDomainName': API_GATEWAY_DOMAIN_NAME,
            'apiGatewayHostedZoneId': API_GATEWAY_HOSTED_ZONE_ID
        })
    )
    
    execution_arn = response['executionArn']
    print(f"Workflow started: {execution_arn}")
    
    return execution_arn


def error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    Create error response
    """
    return {
        'statusCode': status_code,
        'body': json.dumps({
            'error': message
        })
    }
