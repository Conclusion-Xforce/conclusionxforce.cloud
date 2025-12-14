"""
Lambda function to stop Bitwarden ECS container
Handles:
- Stopping ECS task
- Canceling Step Functions execution
- Removing Route53 DNS record

Runtime: Python 3.13
"""

import json
import os
import boto3
from typing import Dict, Any

# AWS clients
ecs = boto3.client('ecs')
route53 = boto3.client('route53')
stepfunctions = boto3.client('stepfunctions')

# Environment variables from CDK
CLUSTER_NAME = os.environ['CLUSTER_NAME']
API_GATEWAY_DOMAIN_NAME = os.environ['API_GATEWAY_DOMAIN_NAME']
API_GATEWAY_HOSTED_ZONE_ID = os.environ['API_GATEWAY_HOSTED_ZONE_ID']
HOSTED_ZONE_ID = os.environ['HOSTED_ZONE_ID']
FQDN = os.environ['FQDN']


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler
    
    Can be called in two ways:
    1. Manual stop via Control API Gateway:
       {
           "sourceIp": "203.0.113.42"  # Optional
       }
    
    2. Step Functions workflow (auto-shutdown):
       {
           "taskArn": "arn:aws:ecs:...",
           "clusterName": "...",
           "executionArn": "..." (optional, for manual stop)
       }
    """
    try:
        task_arn = event.get('taskArn')
        execution_arn = event.get('executionArn')
        
        print(f"Stopping Bitwarden container")
        print(f"Task ARN: {task_arn}")
        
        # If no task ARN provided, find running tasks
        if not task_arn:
            task_arn = find_running_task()
        
        # Stop the ECS task if it exists
        if task_arn:
            stop_ecs_task(task_arn)
        else:
            print("No running task found")
        
        # Remove DNS record
        remove_dns_record()
        
        # Cancel Step Functions execution if provided
        if execution_arn:
            cancel_workflow(execution_arn)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Bitwarden container stopped successfully',
                'taskArn': task_arn
            })
        }
        
    except Exception as e:
        print(f"Error stopping container: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f"Failed to stop container: {str(e)}"
            })
        }


def find_running_task() -> str:
    """
    Find running Bitwarden task in the cluster
    
    Returns:
        str: Task ARN or empty string if not found
    """
    print(f"Looking for running tasks in cluster {CLUSTER_NAME}")
    
    try:
        response = ecs.list_tasks(
            cluster=CLUSTER_NAME,
            desiredStatus='RUNNING'
        )
        
        if response['taskArns']:
            # Return the first running task
            return response['taskArns'][0]
        
        return ''
        
    except Exception as e:
        print(f"Error finding running task: {str(e)}")
        return ''


def stop_ecs_task(task_arn: str) -> None:
    """
    Stop ECS task gracefully
    
    Args:
        task_arn: ECS task ARN to stop
    """
    print(f"Stopping ECS task: {task_arn}")
    
    try:
        ecs.stop_task(
            cluster=CLUSTER_NAME,
            task=task_arn,
            reason='Manual stop or auto-shutdown triggered'
        )
        print("Task stopped successfully")
    except Exception as e:
        print(f"Error stopping task: {str(e)}")
        # Don't raise - continue with cleanup


def remove_dns_record() -> None:
    """
    Remove Route53 Alias record for FQDN
    """
    print(f"Removing DNS record for {FQDN}")
    
    try:
        # Get the current Alias record
        response = route53.list_resource_record_sets(
            HostedZoneId=HOSTED_ZONE_ID,
            StartRecordName=FQDN,
            StartRecordType='A',
            MaxItems='1'
        )
        
        # Check if the record exists and is an Alias record
        if response['ResourceRecordSets']:
            record = response['ResourceRecordSets'][0]
            if (record['Name'].rstrip('.') == FQDN.rstrip('.') and 
                record['Type'] == 'A' and 
                'AliasTarget' in record):
                
                # Delete the Alias record
                route53.change_resource_record_sets(
                    HostedZoneId=HOSTED_ZONE_ID,
                    ChangeBatch={
                        'Changes': [{
                            'Action': 'DELETE',
                            'ResourceRecordSet': record
                        }]
                    }
                )
                print(f"DNS Alias record removed successfully")
            else:
                print(f"DNS record not found or not an Alias record for {FQDN}")
        else:
            print(f"No DNS records found")
            
    except Exception as e:
        print(f"Warning: Failed to remove DNS record: {str(e)}")
        # Don't fail the entire operation if DNS cleanup fails


def cancel_workflow(execution_arn: str) -> None:
    """
    Cancel Step Functions execution
    
    Args:
        execution_arn: Step Functions execution ARN to cancel
    """
    print(f"Canceling Step Functions execution: {execution_arn}")
    
    try:
        stepfunctions.stop_execution(
            executionArn=execution_arn,
            error='ManualStop',
            cause='User requested manual stop'
        )
        print("Workflow canceled successfully")
    except Exception as e:
        print(f"Error canceling workflow: {str(e)}")
        # Don't raise - execution might already be completed
