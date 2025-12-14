# Bitwarden Lite on AWS - Container-Based On-Demand Architecture (CDK TypeScript)

## Overview

This design replaces the VM-based Bitwarden deployment with a containerized Bitwarden Lite solution that runs only when needed, significantly reducing costs while maintaining security. Built with AWS CDK using TypeScript for infrastructure as code.

## Architecture Components

### 1. Container Infrastructure
- **AWS ECS Fargate** - Serverless container platform (no VM management)
- **Bitwarden Lite Container** - MySQL-based version with dual HTTP/HTTPS support
- **Aurora Serverless v2 MySQL** - Scalable, pay-per-use database that auto-scales to zero

### 2. On-Demand Control
- **Lambda Function** - Starts the ECS task and triggers Step Functions
- **Step Functions** - Orchestrates auto-shutdown workflow with configurable wait time
- **API Gateway** - REST endpoint for triggering Lambda
- **Shell Script** - Local script to start container and access Bitwarden

### 3. Security Layers
- **Security Group** - Restricts access to your current IP only (ports 8080 and 8443)
- **VPC** - Private networking with public subnet for container
- **Secrets Manager** - Stores database credentials, Bitwarden config, and API keys
- **IAM Roles** - Least privilege access for all components

### 4. Cost Optimization
- **Step Functions Auto-shutdown** - Orchestrated workflow stops container after idle time
- **Aurora Serverless v2** - Scales to 0.5 ACU when idle, pauses when not in use
- **Fargate Spot** (optional) - Up to 70% cost savings for non-critical workloads
- **Pay-per-use** - Only charged when container is running

## Detailed Architecture

```
┌─────────────────┐
│  Local Machine  │
│                 │
│  Shell Script   │
└────────┬────────┘
         │
         │ 1. Trigger start (with current IP)
         ▼
┌──────────────────────────────────────────────────────────────┐
│                         AWS Cloud                            │
│                                                              │
│  ┌──────────────┐      ┌──────────────────────────────┐    │
│  │ API Gateway  │─────▶│  Lambda (Start Function)     │    │
│  │  (REST API)  │      │  - Start ECS Task            │    │
│  └──────────────┘      │  - Update SG (8080 & 8443)   │    │
│                        │  - Trigger Step Functions    │    │
│                        │  - Return endpoint           │    │
│                        └──────────┬───────────────────┘    │
│                                   │                         │
│                                   ▼                         │
│                        ┌──────────────────────────────┐    │
│                        │  Step Functions Workflow     │    │
│                        │  1. Wait (30 min)            │    │
│                        │  2. Check ECS task status    │    │
│                        │  3. Stop ECS task            │    │
│                        │  4. Clean up SG rules        │    │
│                        └──────────────────────────────┘    │
│                                                              │
│  ┌───────────────────────────────────────────────────┐     │
│  │           ECS Fargate Cluster                     │     │
│  │                                                   │     │
│  │  ┌─────────────────────────────────────────┐    │     │
│  │  │  Bitwarden Lite Container               │    │     │
│  │  │  - Port 8080 (HTTP)                     │    │     │
│  │  │  - Port 8443 (HTTPS)                    │    │     │
│  │  │  - Connects to Aurora MySQL             │    │     │
│  │  │  - EFS for attachments/config           │    │     │
│  │  └──────────────┬──────────────────────────┘    │     │
│  └─────────────────┼───────────────────────────────┘     │
│                    │                                       │
│         ┌──────────┴──────────┐                          │
│         ▼                     ▼                          │
│  ┌──────────────┐    ┌─────────────────────────┐       │
│  │     EFS      │    │  Aurora Serverless v2   │       │
│  │ - attachments│    │  MySQL Database         │       │
│  │ - config     │    │  - Auto-scales          │       │
│  │ - logs       │    │  - Min: 0.5 ACU         │       │
│  └──────────────┘    │  - Max: 1 ACU           │       │
│                      └─────────────────────────┘       │
│                                                         │
│  ┌────────────────────────────────┐                    │
│  │  Security Groups               │                    │
│  │  Container SG:                 │                    │
│  │  - Ingress: Your IP only       │                    │
│  │  - Port 8080 (HTTP)            │                    │
│  │  - Port 8443 (HTTPS)           │                    │
│  │                                │                    │
│  │  Database SG:                  │                    │
│  │  - Ingress: Container SG only  │                    │
│  │  - Port 3306 (MySQL)           │                    │
│  └────────────────────────────────┘                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Workflow

### Starting Bitwarden
1. Run local shell script: `./bitwarden-start.sh`
2. Script calls API Gateway with authentication token
3. Lambda function (Start):
   - Retrieves your current public IP
   - Updates Security Group to allow your IP on ports 8080 and 8443
   - Starts ECS Fargate task
   - Triggers Step Functions workflow for auto-shutdown
   - Waits for task to be healthy
   - Returns the public endpoint URLs (HTTP and HTTPS)
4. Script displays both URLs:
   - `http://<ip>:8080` (HTTP)
   - `https://<ip>:8443` (HTTPS)
5. Access your passwords via browser or CLI

### Auto-Shutdown (Step Functions)
1. Step Functions workflow starts when container launches
2. **Wait State**: Pauses for configurable duration (default 30 minutes)
3. **Check State**: Lambda checks if task is still running
4. **Stop State**: Lambda stops the ECS task
5. **Cleanup State**: Lambda removes IP from Security Group
6. Aurora database auto-scales down to minimum or pauses
7. Billing stops for compute resources

### Manual Shutdown
- Run: `./bitwarden-stop.sh`
- Calls API Gateway stop endpoint
- Lambda cancels the Step Functions execution
- Stops the ECS task immediately
- Cleans up Security Group rules

## Cost Comparison

### Current VM-Based (Example)
- **t3.medium** (2 vCPU, 4GB RAM): ~$30/month (24/7)
- **EBS Storage** (20GB): ~$2/month
- **Total**: ~$32/month

### New Container-Based (Estimated)
- **Fargate** (0.5 vCPU, 1GB RAM): $0.04856/hour
  - Used 2 hours/day: ~$3/month
  - Used 1 hour/day: ~$1.50/month
- **Aurora Serverless v2** (0.5-1 ACU): $0.12/hour per ACU
  - Active 2 hours/day at 0.5 ACU: ~$3.60/month
  - Idle time (minimal cost): ~$0.50/month
  - **Subtotal**: ~$4/month
- **EFS Storage** (2GB for attachments): ~$0.60/month
- **Lambda**: <$0.20/month (free tier covers most usage)
- **API Gateway**: <$0.10/month (free tier covers most usage)
- **Step Functions**: <$0.10/month (4,000 free state transitions/month)
- **Total**: ~$6-9/month (70-80% cost reduction)

**Note**: Aurora adds ~$3-4/month vs SQLite, but provides better reliability, automatic backups, and easier scaling. Can switch to Aurora Serverless v1 (pauses completely) for even lower costs if v2 pricing is a concern.

## Security Features

### 1. IP Whitelisting
- Security Group dynamically updated with your current IP
- Ports 8080 (HTTP) and 8443 (HTTPS) both restricted to your IP
- Only your machine can access the container
- Automatic cleanup of old IP rules via Step Functions

### 2. Authentication Layers
- API Gateway requires API key or IAM authentication
- Bitwarden requires master password
- Database credentials stored in Secrets Manager
- Optional: Add AWS Cognito for additional auth layer

### 3. Encryption
- Aurora encrypted at rest (AWS KMS)
- EFS encrypted at rest (AWS KMS)
- HTTPS/TLS on port 8443 for encrypted transit
- Secrets Manager for database credentials and sensitive data

### 4. Network Isolation
- Container runs in VPC public subnet (for direct access)
- Database in private subnet (no internet access)
- Database Security Group only allows container access
- Optional: Use private subnet with NAT Gateway for enhanced security

### 5. Audit Trail
- CloudWatch Logs for all Lambda invocations
- Step Functions execution history
- ECS task logs
- Aurora query logs (optional)
- CloudTrail for API calls

## Implementation Approach

### Selected Architecture
- **Public subnet** with Security Group IP restriction (ports 8080 & 8443)
- **Dual protocol support**: HTTP (8080) and HTTPS (8443) simultaneously
- **Aurora Serverless v2 MySQL** in private subnet
- **Step Functions** for orchestrated auto-shutdown
- **CDK TypeScript** for infrastructure as code
- **Direct ECS task access** (no load balancer needed)

### Why This Works
- **Dual ports**: Bitwarden Lite supports both protocols simultaneously
- **Self-signed cert**: HTTPS on 8443 uses self-signed certificate (acceptable for personal use)
- **Cost-effective**: No ALB needed (~$16/month savings)
- **Simple**: Direct access to container IP
- **Secure**: IP whitelisting + VPC + database isolation

### Alternative: Custom Domain with ACM
If you want a proper SSL certificate:
- Add Route53 hosted zone
- Use ACM for free SSL certificate
- Update Lambda to create DNS record pointing to container IP
- Configure Bitwarden with your domain
- **Additional cost**: ~$0.50/month for Route53

## Bitwarden Lite Specifics

### Container Configuration
```dockerfile
# Bitwarden Lite supports both HTTP and HTTPS simultaneously
# Port 8080: HTTP
# Port 8443: HTTPS (self-signed certificate)
# Uses MySQL database (Aurora Serverless v2)
# Minimal resource requirements: 0.5 vCPU, 1GB RAM
```

### Environment Variables
```bash
BW_DOMAIN=<your-ip-or-domain>
BW_HTTP_PORT=8080
BW_HTTPS_PORT=8443

# Database configuration
BW_DATABASE_PROVIDER=mysql
BW_DATABASE_HOST=<aurora-endpoint>
BW_DATABASE_PORT=3306
BW_DATABASE_NAME=bitwarden
BW_DATABASE_USERNAME=<from-secrets-manager>
BW_DATABASE_PASSWORD=<from-secrets-manager>

# Security
BW_ENABLE_ADMIN=false
BW_LOG_LEVEL=info

# SSL (self-signed for personal use)
BW_SSL_CERT=/ssl/certificate.crt
BW_SSL_KEY=/ssl/private.key
```

### Data Persistence
- **Aurora MySQL**: All vault data, users, organizations
- **EFS Mount**: 
  - `/attachments/` - File attachments
  - `/ssl/` - SSL certificates
  - `/logs/` - Application logs
  - `/config/` - Configuration files

## Shell Script Features

### bitwarden-start.sh
```bash
#!/bin/bash
# Features:
# - Get current public IP
# - Call API Gateway to start container
# - Poll for container readiness
# - Display both HTTP and HTTPS URLs
# - Optional: Open browser to HTTPS URL automatically
# - Show estimated auto-shutdown time
```

Example output:
```
Starting Bitwarden container...
Your IP: 203.0.113.42
Container starting... (this may take 30-60 seconds)
✓ Container is ready!

Access Bitwarden at:
  HTTP:  http://54.123.45.67:8080
  HTTPS: https://54.123.45.67:8443 (self-signed cert)

Auto-shutdown in 30 minutes.
To stop manually, run: ./bitwarden-stop.sh
```

### bitwarden-stop.sh
```bash
#!/bin/bash
# Features:
# - Call API Gateway to stop container
# - Cancel Step Functions execution
# - Confirm shutdown
# - Display cost savings message
```

## Monitoring & Alerts

### CloudWatch Metrics
- ECS task CPU/Memory utilization
- Container start/stop events
- Lambda execution duration and errors
- API Gateway request count

### Optional Alerts
- SNS notification when container starts
- Alert if container runs >4 hours (cost control)
- Alert on failed starts

## Backup Strategy

### Automated Backups
- **Aurora Automated Backups**: Daily snapshots, 7-day retention (included)
- **Aurora Continuous Backup**: Point-in-time recovery (optional)
- **AWS Backup for EFS**: Daily snapshots for attachments
- Retention: 7 days
- Cost: ~$0.05/GB/month for EFS backups

### Manual Export
- Script to export Bitwarden vault to JSON
- Store encrypted backup in S3
- Lifecycle policy to Glacier after 30 days
- Lambda function for scheduled exports (optional)

## Migration from VM

### Steps
1. Export data from current Bitwarden instance
2. Deploy new infrastructure using CDK (`cdk deploy`)
3. Start container via shell script
4. Import data to new MySQL-based instance
5. Test thoroughly (verify all passwords, attachments)
6. Update shell scripts with new API Gateway endpoint
7. Decommission old VM

### Data Export/Import
```bash
# Export from old instance (SQLite-based)
bw export --format json --output backup.json

# Import to new instance (MySQL-based)
# Start the container first
./bitwarden-start.sh

# Then import
bw config server https://<container-ip>:8443
bw login
bw import bitwarden backup.json
```

### Database Migration Considerations
- Bitwarden Lite handles MySQL schema automatically
- First startup creates all necessary tables
- Import process works regardless of backend database
- Attachments need to be copied to EFS mount

## CDK TypeScript Stack Structure

### Project Organization
```
bitwarden-cdk/
├── bin/
│   └── bitwarden-app.ts          # CDK app entry point
├── lib/
│   ├── bitwarden-stack.ts        # Main stack
│   ├── constructs/
│   │   ├── network.ts            # VPC, subnets, security groups
│   │   ├── database.ts           # Aurora Serverless v2
│   │   ├── storage.ts            # EFS file system
│   │   ├── container.ts          # ECS Fargate task definition
│   │   ├── api.ts                # API Gateway + Lambda
│   │   └── orchestration.ts     # Step Functions workflow
│   └── lambda/
│       ├── start-container/      # Start Lambda handler
│       ├── stop-container/       # Stop Lambda handler
│       └── check-task-status/    # Step Functions task checker
├── scripts/
│   ├── bitwarden-start.sh        # Client start script
│   └── bitwarden-stop.sh         # Client stop script
├── cdk.json
├── package.json
└── tsconfig.json
```

### CDK Constructs Needed

1. **Network Construct** (`network.ts`)
   - VPC with public and private subnets
   - Security groups (container, database)
   - NAT Gateway (optional)

2. **Database Construct** (`database.ts`)
   - Aurora Serverless v2 MySQL cluster
   - Secrets Manager for credentials
   - Subnet group for private subnets

3. **Storage Construct** (`storage.ts`)
   - EFS file system
   - Mount targets
   - Access points

4. **Container Construct** (`container.ts`)
   - ECS Fargate cluster
   - Task definition with dual port mapping (8080, 8443)
   - Container image configuration
   - IAM roles

5. **API Construct** (`api.ts`)
   - API Gateway REST API
   - Lambda functions (start, stop)
   - API key for authentication

6. **Orchestration Construct** (`orchestration.ts`)
   - Step Functions state machine
   - Wait state (configurable timeout)
   - Task status checker Lambda
   - Stop task Lambda
   - Cleanup Lambda

## Next Steps

1. **Initialize CDK Project**
   ```bash
   mkdir bitwarden-cdk && cd bitwarden-cdk
   cdk init app --language typescript
   npm install @aws-cdk/aws-ec2 @aws-cdk/aws-ecs @aws-cdk/aws-rds @aws-cdk/aws-efs @aws-cdk/aws-stepfunctions
   ```

2. **Create CDK Constructs** (in order)
   - Network construct (VPC, subnets, security groups)
   - Database construct (Aurora Serverless v2)
   - Storage construct (EFS)
   - Container construct (ECS Fargate)
   - API construct (API Gateway + Lambda)
   - Orchestration construct (Step Functions)

3. **Implement Lambda Functions**
   - Start container handler (TypeScript/Node.js)
   - Stop container handler
   - Task status checker for Step Functions

4. **Create Step Functions Workflow**
   - Wait state (30 minutes)
   - Check task status
   - Stop task
   - Cleanup security group

5. **Build/Configure Container**
   - Use official Bitwarden Lite image
   - Configure for MySQL
   - Set up dual port support (8080, 8443)
   - Generate self-signed SSL certificate

6. **Create Shell Scripts**
   - bitwarden-start.sh
   - bitwarden-stop.sh

7. **Deploy and Test**
   ```bash
   cdk synth    # Validate CloudFormation
   cdk deploy   # Deploy to AWS
   ```

8. **Migrate Data**
   - Export from old instance
   - Import to new instance
   - Verify all data

9. **Decommission Old VM**

## Estimated Implementation Time

- **CDK Infrastructure**: 6-8 hours
- **Lambda Functions**: 3-4 hours
- **Step Functions Workflow**: 2-3 hours
- **Container Configuration**: 2-3 hours
- **Shell Scripts**: 1-2 hours
- **Testing & Migration**: 2-3 hours
- **Total**: 16-23 hours (2-3 days of focused work)

## Step Functions Workflow Details

### State Machine Definition
```json
{
  "Comment": "Auto-shutdown workflow for Bitwarden container",
  "StartAt": "WaitForTimeout",
  "States": {
    "WaitForTimeout": {
      "Type": "Wait",
      "Seconds": 1800,
      "Next": "CheckTaskStatus"
    },
    "CheckTaskStatus": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:function:CheckTaskStatus",
      "Next": "IsTaskRunning"
    },
    "IsTaskRunning": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.taskStatus",
          "StringEquals": "RUNNING",
          "Next": "StopTask"
        }
      ],
      "Default": "AlreadyStopped"
    },
    "StopTask": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:function:StopTask",
      "Next": "CleanupSecurityGroup"
    },
    "CleanupSecurityGroup": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:function:CleanupSecurityGroup",
      "End": true
    },
    "AlreadyStopped": {
      "Type": "Succeed"
    }
  }
}
```

### Benefits of Step Functions
- **Reliable**: Automatic retries and error handling
- **Visible**: See execution history in AWS Console
- **Flexible**: Easy to adjust timeout or add steps
- **Cancellable**: Manual stop can cancel the workflow
- **Cost-effective**: First 4,000 state transitions free per month

## Additional Considerations

### Domain Name (Optional)
- Use Route53 for DNS if you want a friendly URL
- Lambda can update Route53 record to point to current container IP
- Use ACM for free SSL certificate with your domain
- Cost: $0.50/month per hosted zone

### Aurora Serverless v1 vs v2
- **v2 (Recommended)**: Faster scaling, scales to 0.5 ACU minimum
- **v1**: Can pause completely (0 cost when idle), but slower cold starts
- For maximum cost savings with infrequent use, consider v1

### Multi-Region (Future Enhancement)
- Aurora Global Database for cross-region replication
- EFS replication to another region
- Route53 health checks for failover
- Adds complexity and cost

### CLI Access
- Bitwarden CLI can be used instead of web interface
- Faster for password retrieval
- Can be integrated into shell script for direct password access
- Example: `./bitwarden-start.sh && bw get password "GitHub"`

### Session Management
- Keep browser session alive to avoid re-authentication
- Use Bitwarden browser extension with self-hosted server
- Configure session timeout in Bitwarden settings
- Consider longer timeout since container auto-stops anyway

## Conclusion

This architecture provides a cost-effective, secure, and convenient way to run Bitwarden Lite on AWS with the following improvements over the original design:

✅ **Step Functions** for reliable auto-shutdown (no sidecar needed)
✅ **Dual HTTP/HTTPS** support on ports 8080 and 8443
✅ **Aurora Serverless v2 MySQL** for better reliability and backups
✅ **CDK TypeScript** for type-safe infrastructure as code

The on-demand nature means you only pay for what you use (70-80% cost reduction), while maintaining strong security through IP whitelisting, VPC isolation, and encryption. The CDK approach provides excellent developer experience with TypeScript type checking and reusable constructs.
