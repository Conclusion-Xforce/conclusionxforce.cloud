# Deployment Checklist

Use this checklist to track your progress deploying Bitwarden Lite on AWS.

## Pre-Deployment

### AWS Account Setup
- [ ] AWS account created
- [ ] AWS CLI installed
- [ ] AWS CLI configured with credentials
- [ ] AWS CDK installed (`npm install -g aws-cdk`)
- [ ] Appropriate IAM permissions verified

### Domain and Certificate
- [ ] Domain name registered
- [ ] Route53 hosted zone created
- [ ] Hosted zone name noted: `_________________`
- [ ] ACM certificate requested in **us-east-1**
- [ ] Certificate domain: `_________________`
- [ ] DNS validation CNAME added to Route53
- [ ] Certificate status: "Issued" ✓

### Local Setup
- [ ] Node.js installed (v18 or later)
- [ ] TypeScript installed
- [ ] Python 3.13 installed (for local Lambda testing)
- [ ] jq installed (for shell scripts)
- [ ] Git installed

## CDK Project Setup

### Initialize Project
- [ ] Created project directory: `bitwarden-cdk`
- [ ] Ran `cdk init app --language typescript`
- [ ] Installed dependencies: `npm install aws-cdk-lib constructs`
- [ ] Copied `cdk.json.example` to `cdk.json`
- [ ] Updated `bitwardenFqdn` in cdk.json
- [ ] Updated `hostedZoneName` in cdk.json
- [ ] Configured `autoShutdownMinutes` (default: 30)

### Lambda Functions
- [ ] Created `lib/lambda/start-container/` directory
- [ ] Copied `lambda-start-container.py` to `lib/lambda/start-container/index.py`
- [ ] Copied `requirements.txt` to `lib/lambda/start-container/`
- [ ] Created `lib/lambda/stop-container/` directory
- [ ] Copied `lambda-stop-container.py` to `lib/lambda/stop-container/index.py`
- [ ] Copied `requirements.txt` to `lib/lambda/stop-container/`
- [ ] Created `lib/lambda/cleanup/` directory
- [ ] Copied `lambda-cleanup.py` to `lib/lambda/cleanup/index.py`
- [ ] Copied `requirements.txt` to `lib/lambda/cleanup/`

### CDK Constructs
- [ ] Created `lib/constructs/` directory
- [ ] Implemented `network.ts` (VPC, subnets, security groups)
- [ ] Implemented `database.ts` (Aurora Serverless v2)
- [ ] Implemented `storage.ts` (EFS)
- [ ] Implemented `container.ts` (ECS Fargate)
- [ ] Implemented `api-gateway.ts` (HTTP API + VPC Link)
- [ ] Implemented `control-api.ts` (REST API)
- [ ] Implemented `dns.ts` (Route53)
- [ ] Implemented `orchestration.ts` (Step Functions)

### Main Stack
- [ ] Updated `lib/bitwarden-stack.ts` to use all constructs
- [ ] Added CDK outputs for important values
- [ ] Reviewed stack code for errors

## Deployment

### Pre-Deployment Checks
- [ ] Ran `cdk synth` successfully
- [ ] Reviewed generated CloudFormation template
- [ ] Checked for any security warnings
- [ ] Verified all parameters are correct

### Bootstrap (First Time Only)
- [ ] Ran `cdk bootstrap` in target account/region
- [ ] Bootstrap completed successfully

### Deploy Stack
- [ ] Ran `cdk deploy`
- [ ] Reviewed changes and confirmed
- [ ] Deployment completed successfully (10-15 minutes)
- [ ] Noted CDK outputs:
  - Control API URL: `_________________`
  - Control API Key: `_________________`
  - Bitwarden URL: `_________________`
  - Cluster Name: `_________________`

## Post-Deployment Configuration

### Shell Scripts
- [ ] Copied `bitwarden-start.sh` to local directory
- [ ] Updated `CONTROL_API_URL` in `bitwarden-start.sh`
- [ ] Updated `API_KEY` in `bitwarden-start.sh`
- [ ] Made script executable: `chmod +x bitwarden-start.sh`
- [ ] Copied `bitwarden-stop.sh` to local directory
- [ ] Updated `CONTROL_API_URL` in `bitwarden-stop.sh`
- [ ] Updated `API_KEY` in `bitwarden-stop.sh`
- [ ] Made script executable: `chmod +x bitwarden-stop.sh`

## Testing

### Initial Test
- [ ] Ran `./bitwarden-start.sh`
- [ ] Script completed without errors
- [ ] Waited 30-60 seconds for container to start
- [ ] Checked DNS: `dig bitwarden.example.com`
- [ ] DNS resolves to API Gateway
- [ ] Opened `https://bitwarden.example.com` in browser
- [ ] Bitwarden login page loads
- [ ] No SSL certificate warnings

### Functionality Test
- [ ] Created Bitwarden account
- [ ] Logged in successfully
- [ ] Created test password entry
- [ ] Verified password entry saved
- [ ] Logged out and logged back in
- [ ] Test password entry still exists

### Auto-Shutdown Test
- [ ] Waited for auto-shutdown timeout (30 minutes)
- [ ] Verified container stopped automatically
- [ ] Checked Step Functions execution completed
- [ ] Verified DNS record removed
- [ ] Confirmed ECS task stopped

### Manual Stop Test
- [ ] Started container again: `./bitwarden-start.sh`
- [ ] Ran `./bitwarden-stop.sh` before timeout
- [ ] Verified container stopped immediately
- [ ] Checked Step Functions execution canceled
- [ ] Verified DNS record removed

## Monitoring Setup

### CloudWatch
- [ ] Verified Lambda logs are being created
- [ ] Verified ECS task logs are being created
- [ ] Verified API Gateway logs are being created
- [ ] Set up CloudWatch dashboard (optional)

### Alarms (Optional)
- [ ] Created alarm for Lambda errors
- [ ] Created alarm for ECS task failures
- [ ] Created alarm for API Gateway 5xx errors
- [ ] Created alarm for long-running containers (cost control)

### Cost Monitoring
- [ ] Set up AWS Budgets alert
- [ ] Configured billing alarm
- [ ] Reviewed Cost Explorer

## Backup Setup

### Aurora Backups
- [ ] Verified automated backups are enabled
- [ ] Checked backup retention period (default: 7 days)
- [ ] Tested point-in-time recovery (optional)

### EFS Backups
- [ ] Set up AWS Backup for EFS (optional)
- [ ] Configured backup schedule
- [ ] Verified backup retention

### Manual Backup
- [ ] Exported Bitwarden vault to JSON
- [ ] Stored backup in secure location
- [ ] Documented backup procedure

## Security Hardening

### IAM
- [ ] Reviewed Lambda execution roles
- [ ] Verified least privilege access
- [ ] Removed unnecessary permissions

### Network
- [ ] Verified container is in private subnet
- [ ] Verified database is in private subnet
- [ ] Checked security group rules
- [ ] Enabled VPC Flow Logs (optional)

### Encryption
- [ ] Verified Aurora encryption at rest
- [ ] Verified EFS encryption at rest
- [ ] Verified Secrets Manager encryption
- [ ] Confirmed HTTPS/TLS on API Gateway

### Audit
- [ ] Enabled CloudTrail (if not already)
- [ ] Configured CloudTrail log retention
- [ ] Set up CloudTrail alerts (optional)

## Documentation

### Internal Documentation
- [ ] Documented deployment process
- [ ] Created runbook for common operations
- [ ] Documented troubleshooting steps
- [ ] Created disaster recovery plan

### Team Knowledge
- [ ] Shared Control API credentials securely
- [ ] Documented how to start/stop container
- [ ] Explained auto-shutdown behavior
- [ ] Provided access to monitoring dashboards

## Migration (If Applicable)

### Data Export from Old System
- [ ] Exported data from old Bitwarden VM
- [ ] Verified export file integrity
- [ ] Backed up export file

### Data Import
- [ ] Started new Bitwarden container
- [ ] Imported data to new instance
- [ ] Verified all passwords imported
- [ ] Verified all attachments imported
- [ ] Tested password retrieval

### Cutover
- [ ] Updated bookmarks to new URL
- [ ] Updated browser extensions
- [ ] Updated mobile apps
- [ ] Tested from all devices
- [ ] Decommissioned old VM

## Optimization

### Cost Optimization
- [ ] Reviewed actual usage patterns
- [ ] Adjusted auto-shutdown timeout if needed
- [ ] Considered Fargate Spot (if acceptable)
- [ ] Reviewed Aurora capacity settings

### Performance
- [ ] Measured container startup time
- [ ] Measured API Gateway latency
- [ ] Optimized if needed

## Maintenance Plan

### Regular Tasks
- [ ] Weekly: Check CloudWatch Logs for errors
- [ ] Monthly: Review costs in Cost Explorer
- [ ] Monthly: Test backup and restore
- [ ] Quarterly: Review and rotate API keys
- [ ] Quarterly: Update Lambda runtimes if needed
- [ ] Yearly: Review and update architecture

### Update Procedures
- [ ] Documented how to update Lambda functions
- [ ] Documented how to update ECS task definition
- [ ] Documented how to update CDK stack
- [ ] Created rollback procedure

## Final Checks

- [ ] All tests passed
- [ ] Monitoring is working
- [ ] Backups are configured
- [ ] Documentation is complete
- [ ] Team is trained
- [ ] Old system decommissioned (if applicable)

## Success Criteria

- [ ] Bitwarden accessible via HTTPS
- [ ] Auto-shutdown working correctly
- [ ] Manual start/stop working
- [ ] Costs within expected range (~$16-18/month)
- [ ] No security warnings or issues
- [ ] All data migrated successfully (if applicable)

---

## Notes

Use this section to track any issues, decisions, or important information:

```
Date: ___________
Notes:




```

---

## Completion

**Deployment completed on**: ___________

**Deployed by**: ___________

**Production ready**: [ ] Yes [ ] No

**Sign-off**: ___________
