"""
Lambda function to cleanup resources after ECS task stops
Called by Step Functions workflow
Handles:
- Removing Route53 DNS record

Runtime: Python 3.13
"""

import json
import os
import boto3
from typing import Dict, Any

# AWS clients
route53 = boto3.client('route53')


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler
    
    Expected event from Step Functions:
    {
        "taskArn": "arn:aws:ecs:...",
        "hostedZoneId": "Z1234567890ABC",
        "fqdn": "bitwarden.example.com",
        "apiGatewayDomainName": "d-abc123.execute-api.us-east-1.amazonaws.com",
        "apiGatewayHostedZoneId": "Z2FDTNDATAQYW2"
    }
    """
    try:
        hosted_zone_id = event.get('hostedZoneId')
        fqdn = event.get('fqdn')
        api_gateway_domain = event.get('apiGatewayDomainName')
        api_gateway_zone_id = event.get('apiGatewayHostedZoneId')
        
        if not all([hosted_zone_id, fqdn]):
            print("Missing required parameters, skipping cleanup")
            return success_response("Cleanup skipped - missing parameters")
        
        print(f"Cleaning up resources for {fqdn}")
        
        # Remove DNS record
        remove_dns_record(hosted_zone_id, fqdn, api_gateway_domain, api_gateway_zone_id)
        
        return success_response("Cleanup completed successfully")
        
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")
        # Don't fail - cleanup is best-effort
        return success_response(f"Cleanup completed with warnings: {str(e)}")


def remove_dns_record(hosted_zone_id: str, fqdn: str, 
                     api_gateway_domain: str, api_gateway_zone_id: str) -> None:
    """
    Remove Route53 Alias record for FQDN
    
    Args:
        hosted_zone_id: Route53 hosted zone ID
        fqdn: Fully qualified domain name
        api_gateway_domain: API Gateway domain name
        api_gateway_zone_id: API Gateway hosted zone ID
    """
    print(f"Removing DNS record for {fqdn}")
    
    try:
        # Get the current Alias record
        response = route53.list_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            StartRecordName=fqdn,
            StartRecordType='A',
            MaxItems='1'
        )
        
        # Check if the record exists and is an Alias record
        if response['ResourceRecordSets']:
            record = response['ResourceRecordSets'][0]
            if (record['Name'].rstrip('.') == fqdn.rstrip('.') and 
                record['Type'] == 'A' and 
                'AliasTarget' in record):
                
                # Delete the Alias record
                route53.change_resource_record_sets(
                    HostedZoneId=hosted_zone_id,
                    ChangeBatch={
                        'Changes': [{
                            'Action': 'DELETE',
                            'ResourceRecordSet': record
                        }]
                    }
                )
                print(f"DNS Alias record removed successfully")
            else:
                print(f"DNS record not found or not an Alias record for {fqdn}")
        else:
            print(f"No DNS records found for {fqdn}")
            
    except Exception as e:
        print(f"Warning: Failed to remove DNS record: {str(e)}")
        # Don't raise - cleanup is best-effort


def success_response(message: str) -> Dict[str, Any]:
    """
    Create success response
    """
    return {
        'statusCode': 200,
        'message': message
    }
