# Deployment Guide

## Prerequisites

### 1. AWS Account Setup
- AWS account with appropriate permissions
- AWS CLI installed and configured
- AWS CDK installed: `npm install -g aws-cdk`

### 2. Create ACM Certificate (REQUIRED)

**Important**: Certificate must be in **us-east-1** region for API Gateway custom domains.

```bash
# Request certificate
aws acm request-certificate \
  --domain-name bitwarden.example.com \
  --validation-method DNS \
  --region us-east-1

# Or use wildcard
aws acm request-certificate \
  --domain-name "*.example.com" \
  --validation-method DNS \
  --region us-east-1
```

**Validate the certificate:**
1. Go to AWS Console → Certificate Manager (us-east-1)
2. Click on the certificate
3. Copy the CNAME record
4. Add it to your Route53 hosted zone
5. Wait for status to change to "Issued" (can take 5-30 minutes)

### 3. Verify Route53 Hosted Zone

```bash
# List hosted zones
aws route53 list-hosted-zones

# Note your hosted zone ID and name
```

## Step-by-Step Deployment

### Step 1: Initialize CDK Project

```bash
# Create project directory
mkdir bitwarden-cdk
cd bitwarden-cdk

# Initialize CDK app
cdk init app --language typescript

# Install dependencies
npm install aws-cdk-lib constructs
```

### Step 2: Configure Parameters

Copy the example configuration:
```bash
cp cdk.json.example cdk.json
```

Edit `cdk.json` and update:
```json
{
  "context": {
    "bitwardenFqdn": "bitwarden.yourdomain.com",
    "hostedZoneName": "yourdomain.com",
    "autoShutdownMinutes": 30,
    "enableSpot": false,
    "auroraMinCapacity": 0.5,
    "auroraMaxCapacity": 1
  }
}
```

### Step 3: Copy Lambda Functions

```bash
# Create Lambda directories
mkdir -p lib/lambda/start-container
mkdir -p lib/lambda/stop-container
mkdir -p lib/lambda/cleanup

# Copy Lambda functions
cp lambda-start-container.py lib/lambda/start-container/index.py
cp lambda-stop-container.py lib/lambda/stop-container/index.py
cp lambda-cleanup.py lib/lambda/cleanup/index.py

# Copy requirements to each Lambda directory
cp requirements.txt lib/lambda/start-container/
cp requirements.txt lib/lambda/stop-container/
cp requirements.txt lib/lambda/cleanup/
```

### Step 4: Create CDK Constructs

Create the following files in `lib/constructs/`:

1. **network.ts** - VPC, subnets, security groups
2. **database.ts** - Aurora Serverless v2
3. **storage.ts** - EFS file system
4. **container.ts** - ECS Fargate task + service
5. **api-gateway.ts** - HTTP API with custom domain + VPC Link
6. **control-api.ts** - REST API for start/stop
7. **dns.ts** - Route53 record management
8. **orchestration.ts** - Step Functions with native ECS

See `bitwarden-lite-aws-design.md` for detailed implementation of each construct.

### Step 5: Bootstrap CDK (First Time Only)

```bash
# Bootstrap CDK in your account/region
cdk bootstrap aws://ACCOUNT-ID/REGION
```

### Step 6: Synthesize CloudFormation

```bash
# Generate CloudFormation template
cdk synth

# Review the generated template
cat cdk.out/BitwardenStack.template.json | jq '.'
```

### Step 7: Deploy

```bash
# Deploy the stack
cdk deploy

# Confirm the changes when prompted
# This will take 10-15 minutes
```

### Step 8: Get Outputs

After deployment, CDK will output important values:

```
Outputs:
BitwardenStack.ControlApiUrl = https://abc123.execute-api.us-east-1.amazonaws.com/prod
BitwardenStack.ControlApiKey = your-api-key-here
BitwardenStack.BitwardenUrl = https://bitwarden.example.com
BitwardenStack.ClusterName = bitwarden-cluster
```

**Save these values!**

### Step 9: Configure Shell Scripts

Edit `bitwarden-start.sh` and `bitwarden-stop.sh`:

```bash
# Update these values from CDK outputs
CONTROL_API_URL="https://YOUR_CONTROL_API_ID.execute-api.YOUR_REGION.amazonaws.com/prod/start"
API_KEY="YOUR_API_KEY"
```

Make scripts executable:
```bash
chmod +x bitwarden-start.sh bitwarden-stop.sh
```

### Step 10: Test

```bash
# Start Bitwarden
./bitwarden-start.sh

# Wait 30-60 seconds for container to start

# Access Bitwarden
open https://bitwarden.example.com

# Stop Bitwarden (or wait for auto-shutdown)
./bitwarden-stop.sh
```

## Verification

### Check ECS Task
```bash
aws ecs list-tasks --cluster bitwarden-cluster
aws ecs describe-tasks --cluster bitwarden-cluster --tasks TASK_ARN
```

### Check DNS
```bash
dig bitwarden.example.com
nslookup bitwarden.example.com
```

### Check API Gateway
```bash
aws apigatewayv2 get-domain-name --domain-name bitwarden.example.com
```

### Check Step Functions
```bash
aws stepfunctions list-executions --state-machine-arn STATE_MACHINE_ARN
```

## Troubleshooting

### Certificate Not Found
- Ensure certificate is in **us-east-1** region
- Verify certificate status is "Issued"
- Check domain name matches exactly

### DNS Not Resolving
- Wait 30-60 seconds for DNS propagation
- Check Route53 record exists
- Verify hosted zone is correct

### Container Won't Start
- Check ECS task logs in CloudWatch
- Verify security groups allow traffic
- Check Aurora database is accessible
- Verify EFS mount is working

### Can't Access via HTTPS
- Check API Gateway custom domain is configured
- Verify VPC Link is healthy
- Check container is running
- Test with curl: `curl -v https://bitwarden.example.com`

## Monitoring

### CloudWatch Logs
- `/aws/lambda/start-container`
- `/aws/lambda/stop-container`
- `/aws/lambda/cleanup`
- `/aws/ecs/bitwarden`
- `/aws/apigateway/bitwarden`

### CloudWatch Metrics
- ECS task CPU/Memory
- API Gateway requests/latency
- Lambda duration/errors
- Step Functions executions

### Cost Monitoring
```bash
# Check current month costs
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```

## Updating

### Update Lambda Functions
```bash
# Update Lambda code
aws lambda update-function-code \
  --function-name bitwarden-start-container \
  --zip-file fileb://lambda.zip
```

### Update ECS Task
```bash
# Update task definition
aws ecs register-task-definition --cli-input-json file://task-def.json

# Update service
aws ecs update-service \
  --cluster bitwarden-cluster \
  --service bitwarden-service \
  --task-definition bitwarden:NEW_REVISION
```

### Update CDK Stack
```bash
# Make changes to CDK code
# Then deploy
cdk deploy
```

## Cleanup

### Destroy Stack
```bash
# This will delete all resources
cdk destroy

# Confirm when prompted
```

**Note**: Some resources may need manual cleanup:
- ACM certificate (if you want to delete it)
- Route53 hosted zone (if you want to delete it)
- CloudWatch Logs (retained by default)

## Security Best Practices

1. **Rotate API Keys** regularly
2. **Enable CloudTrail** for audit logging
3. **Use AWS Secrets Manager** for sensitive data
4. **Enable VPC Flow Logs** for network monitoring
5. **Set up CloudWatch Alarms** for anomalies
6. **Regular backups** of Aurora database
7. **Keep Lambda runtimes updated**
8. **Review IAM policies** regularly

## Cost Optimization

1. **Use Fargate Spot** (set `enableSpot: true` in cdk.json)
2. **Reduce auto-shutdown timeout** if you use it less
3. **Use Aurora Serverless v1** if you can tolerate slower cold starts
4. **Monitor unused resources** with AWS Cost Explorer
5. **Set up billing alerts**

## Next Steps

1. Set up automated backups
2. Configure monitoring and alerts
3. Set up CI/CD pipeline
4. Document your specific configuration
5. Create runbook for common operations

## Support

For issues or questions:
1. Check `bitwarden-lite-aws-design.md` for architecture details
2. Review `QUICK_REFERENCE.md` for common commands
3. Check CloudWatch Logs for errors
4. Review AWS documentation for specific services
