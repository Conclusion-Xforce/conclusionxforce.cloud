# Quick Reference Guide

## Architecture at a Glance

```
Shell Script → Control API → Lambda → ECS Task (private subnet)
                                ↓
                          Step Functions (native ECS)
                                ↓
                          Auto-shutdown after 30 min

Access: https://bitwarden.example.com
        ↓
    API Gateway HTTP API (custom domain + ACM)
        ↓
    VPC Link → ECS Container (port 8080)
```

## Cost: ~$16-18/month (45-50% savings vs VM)

## Key Improvements

1. **API Gateway HTTP API** instead of ALB → Save $10/month
2. **Native Step Functions ECS integration** → No Lambda for status checks
3. **All files in /clone/aws-bitwarden-lite** → Easy to find

## Files

- `README.md` - Quick start
- `bitwarden-lite-aws-design.md` - Complete docs
- `CHANGES_SUMMARY.md` - What changed and why
- `lambda-start-container.py` - Start Lambda (Python 3.13)
- `lambda-stop-container.py` - Stop Lambda (Python 3.13)
- `lambda-cleanup.py` - Cleanup Lambda (Python 3.13)
- `step-functions-definition.json` - State machine with native ECS
- `requirements.txt` - Python dependencies

## Prerequisites

1. ACM certificate in us-east-1
2. Route53 hosted zone
3. AWS CDK installed

## Deploy

```bash
# 1. Configure
vim cdk.json  # Set bitwardenFqdn, hostedZoneName

# 2. Deploy
cdk deploy

# 3. Start
./bitwarden-start.sh

# 4. Access
open https://bitwarden.example.com
```

## CDK Constructs Needed

1. Network (VPC, subnets, security groups)
2. Database (Aurora Serverless v2)
3. Storage (EFS)
4. Container (ECS Fargate + Service)
5. API Gateway (HTTP API + custom domain + VPC Link)
6. Control API (REST API for start/stop)
7. DNS (Route53)
8. Orchestration (Step Functions with native ECS)

## Lambda Environment Variables

### Start Container
- `CLUSTER_NAME` - ECS cluster name
- `TASK_DEFINITION` - ECS task definition ARN
- `SUBNET_IDS` - Comma-separated private subnet IDs
- `CONTAINER_SECURITY_GROUP_ID` - Container security group
- `STATE_MACHINE_ARN` - Step Functions ARN
- `API_GATEWAY_DOMAIN_NAME` - API Gateway domain
- `API_GATEWAY_HOSTED_ZONE_ID` - API Gateway zone ID
- `HOSTED_ZONE_ID` - Your Route53 zone ID
- `FQDN` - Your domain (e.g., bitwarden.example.com)
- `AUTO_SHUTDOWN_MINUTES` - Timeout (default: 30)

### Stop Container
- `CLUSTER_NAME`
- `API_GATEWAY_DOMAIN_NAME`
- `API_GATEWAY_HOSTED_ZONE_ID`
- `HOSTED_ZONE_ID`
- `FQDN`

### Cleanup
- No environment variables needed (all passed via event)

## Step Functions Input

```json
{
  "taskArn": "arn:aws:ecs:...",
  "clusterName": "bitwarden-cluster",
  "hostedZoneId": "Z1234567890ABC",
  "fqdn": "bitwarden.example.com",
  "apiGatewayDomainName": "d-abc123.execute-api.us-east-1.amazonaws.com",
  "apiGatewayHostedZoneId": "Z2FDTNDATAQYW2"
}
```

## Native ECS Integration

### Describe Tasks
```json
{
  "Type": "Task",
  "Resource": "arn:aws:states:::ecs:describeTasks",
  "Parameters": {
    "Cluster.$": "$.clusterName",
    "Tasks.$": "States.Array($.taskArn)"
  }
}
```

### Stop Task
```json
{
  "Type": "Task",
  "Resource": "arn:aws:states:::ecs:stopTask",
  "Parameters": {
    "Cluster.$": "$.clusterName",
    "Task.$": "$.taskArn",
    "Reason": "Auto-shutdown after timeout"
  }
}
```

## Security Groups

### Container SG
- Ingress: VPC Link only, port 8080
- Egress: Aurora (3306), EFS (2049), AWS services (443)

### Database SG
- Ingress: Container SG only, port 3306
- Egress: None

### VPC Link SG
- Ingress: API Gateway (managed)
- Egress: Container SG, port 8080

## Monitoring

### CloudWatch Metrics
- ECS task CPU/Memory
- API Gateway requests/latency
- Lambda duration/errors
- Step Functions executions

### CloudWatch Logs
- `/aws/lambda/start-container`
- `/aws/lambda/stop-container`
- `/aws/lambda/cleanup`
- `/aws/ecs/bitwarden`
- `/aws/apigateway/bitwarden`

## Troubleshooting

### Container won't start
- Check ECS task logs
- Verify security groups
- Check Aurora connection
- Verify EFS mount

### Can't access via HTTPS
- Check DNS propagation: `dig bitwarden.example.com`
- Verify ACM certificate is in us-east-1
- Check API Gateway custom domain
- Verify VPC Link is healthy

### Auto-shutdown not working
- Check Step Functions execution history
- Verify IAM permissions for ECS actions
- Check CloudWatch Logs for cleanup Lambda

## Useful Commands

```bash
# Check ECS tasks
aws ecs list-tasks --cluster bitwarden-cluster

# Describe task
aws ecs describe-tasks --cluster bitwarden-cluster --tasks <task-arn>

# Check Step Functions executions
aws stepfunctions list-executions --state-machine-arn <arn>

# Check DNS record
dig bitwarden.example.com

# Check API Gateway
aws apigatewayv2 get-domain-name --domain-name bitwarden.example.com

# Check VPC Link
aws apigatewayv2 get-vpc-links
```

## Cost Optimization Tips

1. Use Fargate Spot (up to 70% savings)
2. Reduce auto-shutdown timeout if you use it less
3. Use Aurora Serverless v1 if you can tolerate slower cold starts
4. Consider removing VPC Link if you can use public subnets (not recommended)

## Next Steps

1. Read `bitwarden-lite-aws-design.md` for complete documentation
2. Create ACM certificate in us-east-1
3. Initialize CDK project
4. Implement CDK constructs
5. Deploy and test
6. Migrate data from old VM

## Support

See `bitwarden-lite-aws-design.md` for:
- Detailed architecture diagrams
- Complete CDK implementation guide
- Migration guide
- Backup strategy
- Security best practices
