# Bitwarden Lite on AWS - Container-Based On-Demand Architecture (CDK TypeScript)

## Overview

This design replaces the VM-based Bitwarden deployment with a containerized Bitwarden Lite solution that runs only when needed, significantly reducing costs while maintaining security. Built with AWS CDK using TypeScript for infrastructure as code.

## Architecture Components

### 1. Container Infrastructure
- **AWS ECS Fargate** - Serverless container platform (no VM management)
- **Bitwarden Lite Container** - MySQL-based version (HTTP only, ALB handles HTTPS)
- **Aurora Serverless v2 MySQL** - Scalable, pay-per-use database that auto-scales to zero
- **Application Load Balancer** - Handles HTTPS termination with ACM certificate

### 2. On-Demand Control
- **Lambda Function** - Starts the ECS task and triggers Step Functions
- **Step Functions** - Orchestrates auto-shutdown workflow with configurable wait time
- **API Gateway** - REST endpoint for triggering Lambda
- **Shell Script** - Local script to start container and access Bitwarden

### 3. Security Layers
- **Security Group** - Restricts ALB access to your current IP only (port 443)
- **VPC** - Private networking with public and private subnets
- **ACM Certificate** - Automatic HTTPS with your domain (you provide the certificate)
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
┌──────────────────────────────────────────────────────────────────┐
│                         AWS Cloud                                │
│                                                                  │
│  ┌──────────────┐      ┌──────────────────────────────────┐    │
│  │ API Gateway  │─────▶│  Lambda (Start Function)         │    │
│  │  (REST API)  │      │  - Start ECS Task                │    │
│  └──────────────┘      │  - Update ALB SG (port 443)      │    │
│                        │  - Update Route53                │    │
│                        │  - Trigger Step Functions        │    │
│                        │  - Return HTTPS endpoint         │    │
│                        └──────────┬───────────────────────┘    │
│                                   │                             │
│                                   ▼                             │
│                        ┌──────────────────────────────────┐    │
│                        │  Step Functions Workflow         │    │
│                        │  1. Wait (30 min)                │    │
│                        │  2. Check ECS task status        │    │
│                        │  3. Stop ECS task                │    │
│                        │  4. Clean up SG rules            │    │
│                        │  5. Remove Route53 record        │    │
│                        └──────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  Application Load Balancer                           │      │
│  │  - Port 443 (HTTPS with ACM certificate)             │      │
│  │  - Forwards to ECS task on port 8080                 │      │
│  │  - Security Group: Your IP only                      │      │
│  └──────────────────┬───────────────────────────────────┘      │
│                     │                                           │
│                     ▼                                           │
│  ┌───────────────────────────────────────────────────┐         │
│  │           ECS Fargate Cluster                     │         │
│  │                                                   │         │
│  │  ┌─────────────────────────────────────────┐    │         │
│  │  │  Bitwarden Lite Container               │    │         │
│  │  │  - Port 8080 (HTTP only)                │    │         │
│  │  │  - ALB handles HTTPS termination        │    │         │
│  │  │  - Connects to Aurora MySQL             │    │         │
│  │  │  - EFS for attachments/config           │    │         │
│  │  └──────────────┬──────────────────────────┘    │         │
│  └─────────────────┼───────────────────────────────┘         │
│                    │                                           │
│         ┌──────────┴──────────┐                               │
│         ▼                     ▼                               │
│  ┌──────────────┐    ┌─────────────────────────┐            │
│  │     EFS      │    │  Aurora Serverless v2   │            │
│  │ - attachments│    │  MySQL Database         │            │
│  │ - config     │    │  - Auto-scales          │            │
│  │ - logs       │    │  - Min: 0.5 ACU         │            │
│  └──────────────┘    │  - Max: 1 ACU           │            │
│                      └─────────────────────────┘            │
│                                                              │
│  ┌────────────────────────────────┐                         │
│  │  Security Groups               │                         │
│  │  ALB SG:                       │                         │
│  │  - Ingress: Your IP only       │                         │
│  │  - Port 443 (HTTPS)            │                         │
│  │                                │                         │
│  │  Container SG:                 │                         │
│  │  - Ingress: ALB SG only        │                         │
│  │  - Port 8080 (HTTP)            │                         │
│  │                                │                         │
│  │  Database SG:                  │                         │
│  │  - Ingress: Container SG only  │                         │
│  │  - Port 3306 (MySQL)           │                         │
│  └────────────────────────────────┘                         │
│                                                              │
│  ┌────────────────────────────────┐                         │
│  │  Route53                       │                         │
│  │  A Record: bitwarden.example.  │                         │
│  │  com → ALB DNS name (Alias)    │                         │
│  └────────────────────────────────┘                         │
│                                                              │
│  ┌────────────────────────────────┐                         │
│  │  ACM Certificate               │                         │
│  │  (You provide)                 │                         │
│  │  - *.example.com or            │                         │
│  │  - bitwarden.example.com       │                         │
│  └────────────────────────────────┘                         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
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
- **Application Load Balancer**: $0.0225/hour + $0.008/LCU-hour
  - Base: ~$16.20/month (always running)
  - LCU charges: ~$0.50/month (minimal traffic)
  - **Subtotal**: ~$16.70/month
- **EFS Storage** (2GB for attachments): ~$0.60/month
- **Lambda**: <$0.20/month (free tier covers most usage)
- **API Gateway**: <$0.10/month (free tier covers most usage)
- **Step Functions**: <$0.10/month (4,000 free state transitions/month)
- **Route53**: $0.50/month (if new hosted zone)
- **Total**: ~$25-28/month (15-20% cost reduction)

**Note**: ALB adds ~$17/month but provides proper HTTPS with ACM certificate. This is the trade-off for production-grade security. Aurora adds ~$3-4/month vs SQLite for better reliability and automatic backups.

## Security Features

### 1. IP Whitelisting
- ALB Security Group dynamically updated with your current IP
- Port 443 (HTTPS) restricted to your IP only
- Only your machine can access Bitwarden
- Automatic cleanup of old IP rules via Step Functions

### 2. Authentication Layers
- API Gateway requires API key or IAM authentication
- Bitwarden requires master password
- Database credentials stored in Secrets Manager
- Optional: Add AWS Cognito for additional auth layer

### 3. Encryption
- Aurora encrypted at rest (AWS KMS)
- EFS encrypted at rest (AWS KMS)
- HTTPS/TLS via ALB with ACM certificate (you provide)
- Secrets Manager for database credentials and sensitive data

### 4. Network Isolation
- ALB in public subnets
- Container runs in private subnet (no direct internet access)
- Database in private subnet (no internet access)
- Container Security Group only allows ALB access
- Database Security Group only allows container access

### 5. Audit Trail
- CloudWatch Logs for all Lambda invocations
- Step Functions execution history
- ECS task logs
- Aurora query logs (optional)
- CloudTrail for API calls

## Implementation Approach

### Selected Architecture
- **Application Load Balancer** with ACM certificate (you provide)
- **HTTPS only** (port 443) - ALB terminates SSL
- **Container in private subnet** - HTTP (8080) from ALB only
- **Aurora Serverless v2 MySQL** in private subnet
- **Step Functions** for orchestrated auto-shutdown
- **CDK TypeScript** for infrastructure as code
- **Route53** for DNS management

### Why This Architecture
- **Production-grade HTTPS**: ACM certificate with proper SSL/TLS
- **Secure**: Container not directly exposed to internet
- **Professional**: Access via domain name, not IP
- **Flexible**: Works with wildcard or specific certificates
- **Reliable**: ALB provides health checks and automatic failover

### ACM Certificate Handling
- **You provide**: Create ACM certificate for your domain beforehand
- **CDK discovers**: Looks up existing certificate by domain name
- **Supports**: Both wildcard (*.example.com) and specific (bitwarden.example.com)
- **No creation**: CDK won't create certificate (you manage validation)

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
BW_DOMAIN=<your-fqdn>
BW_HTTP_PORT=8080
# No HTTPS port needed - ALB handles HTTPS termination

# Database configuration
BW_DATABASE_PROVIDER=mysql
BW_DATABASE_HOST=<aurora-endpoint>
BW_DATABASE_PORT=3306
BW_DATABASE_NAME=bitwarden
BW_DATABASE_USERNAME=<from-secrets-manager>
BW_DATABASE_PASSWORD=<from-secrets-manager>

# Security
# Note: BW_ENABLE_ADMIN must remain enabled per Bitwarden Lite documentation
# "Do not disable this service" - required for proper operation
BW_ENABLE_ADMIN=true
BW_LOG_LEVEL=info

# No SSL configuration needed - ALB handles certificate
```

### Data Persistence
- **Aurora MySQL**: All vault data, users, organizations
- **EFS Mount**: 
  - `/attachments/` - File attachments
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
Updating DNS record for bitwarden.example.com...
✓ Container is ready!

Access Bitwarden at: https://bitwarden.example.com

Note: DNS propagation may take 30-60 seconds.
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

### Prerequisites
1. **Create ACM Certificate**:
   - Go to AWS Certificate Manager
   - Request certificate for your domain
   - Complete DNS/email validation
   - Wait for "Issued" status

2. **Verify Route53 Hosted Zone**:
   - Ensure hosted zone exists for your domain
   - Note the hosted zone name (e.g., `example.com`)

### Deployment Steps
1. Deploy new infrastructure using CDK (`cdk deploy`)
2. Start container via shell script
3. Test access via HTTPS URL
4. Verify Bitwarden is accessible

### Data Migration (You Handle)
After infrastructure is deployed and tested:
- Export data from your current Bitwarden VM
- Import to new MySQL-based instance
- Verify all passwords and attachments
- Test thoroughly before decommissioning old VM

**Note**: Migration steps are intentionally left for you to execute when ready.

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
│   │   ├── dns.ts                # Route53 record management
│   │   └── orchestration.ts     # Step Functions workflow
│   └── lambda/
│       ├── start-container/      # Start Lambda handler (Python)
│       │   ├── index.py
│       │   └── requirements.txt
│       ├── stop-container/       # Stop Lambda handler (Python)
│       │   ├── index.py
│       │   └── requirements.txt
│       ├── check-task-status/    # Step Functions task checker (Python)
│       │   └── index.py
│       ├── cleanup-sg/           # Security Group cleanup (Python)
│       │   └── index.py
│       └── update-dns/           # Route53 DNS updater (Python)
│           └── index.py
├── scripts/
│   ├── bitwarden-start.sh        # Client start script
│   └── bitwarden-stop.sh         # Client stop script
├── cdk.json
├── cdk.context.json              # CDK context (gitignored)
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

6. **DNS Construct** (`dns.ts`)
   - Route53 hosted zone lookup
   - A record for FQDN
   - Lambda function to update DNS on container start

7. **Orchestration Construct** (`orchestration.ts`)
   - Step Functions state machine
   - Wait state (configurable timeout)
   - Task status checker Lambda (Python)
   - Stop task Lambda (Python)
   - Cleanup Lambda (Python)
   - DNS cleanup Lambda (Python)

## CDK Parameters and Configuration

### Stack Parameters
The CDK stack accepts the following parameters (via context or environment variables):

```typescript
// cdk.json or pass via -c flag
{
  "bitwardenFqdn": "bitwarden.example.com",  // Your domain name (REQUIRED)
  "hostedZoneName": "example.com",            // Your Route53 hosted zone (REQUIRED)
  "autoShutdownMinutes": 30,                  // Auto-shutdown timeout
  "enableSpot": false,                        // Use Fargate Spot for cost savings
  "auroraMinCapacity": 0.5,                   // Aurora min ACU
  "auroraMaxCapacity": 1                      // Aurora max ACU
}
```

### ACM Certificate Lookup Logic
The CDK will automatically find your ACM certificate using this logic:

```typescript
// 1. First, try to find exact match for FQDN
const exactCert = Certificate.fromLookup(scope, 'ExactCert', {
  domainName: 'bitwarden.example.com'
});

// 2. If not found, try wildcard certificate
const wildcardCert = Certificate.fromLookup(scope, 'WildcardCert', {
  domainName: '*.example.com'
});

// 3. Use whichever is found (exact match preferred)
```

**Supported certificate patterns:**
- Exact match: `bitwarden.example.com`
- Wildcard: `*.example.com`
- Multi-domain: Certificate with both domains

**Note**: Certificate must be in the same AWS region as your deployment.

### Route53 Integration Flow

1. **On Container Start**:
   - Lambda starts ECS task
   - Waits for task to get public IP
   - Updates Route53 A record: `bitwarden.example.com` → `<container-ip>`
   - TTL set to 60 seconds for quick updates
   - Returns FQDN to client

2. **On Container Stop**:
   - Step Functions workflow triggers
   - Stops ECS task
   - Deletes Route53 A record
   - Cleans up Security Group rules

3. **Benefits**:
   - Always access via same URL: `https://bitwarden.example.com:8443`
   - No need to remember changing IPs
   - Can use ACM certificate for proper HTTPS
   - Browser remembers the domain

## Next Steps

1. **Initialize CDK Project**
   ```bash
   mkdir bitwarden-cdk && cd bitwarden-cdk
   cdk init app --language typescript
   npm install @aws-cdk/aws-ec2 @aws-cdk/aws-ecs @aws-cdk/aws-rds @aws-cdk/aws-efs @aws-cdk/aws-stepfunctions @aws-cdk/aws-route53
   ```

2. **Create CDK Constructs** (in order)
   - Network construct (VPC, subnets, security groups)
   - Database construct (Aurora Serverless v2)
   - Storage construct (EFS)
   - Container construct (ECS Fargate)
   - DNS construct (Route53 record management)
   - API construct (API Gateway + Lambda)
   - Orchestration construct (Step Functions)

3. **Implement Lambda Functions** (Python 3.13)
   - Start container handler (`lambda/start-container/index.py`)
     - Update ALB Security Group (port 443 only)
     - Start ECS task in private subnet
     - Update Route53 Alias record to ALB
     - Trigger Step Functions workflow
   - Stop container handler (`lambda/stop-container/index.py`)
     - Stop ECS task
     - Clean up ALB Security Group rules
     - Remove Route53 Alias record
     - Cancel Step Functions execution
   - Task status checker (`lambda/check-task-status/index.py`)
     - Check if task is still running
     - Used by Step Functions workflow

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

### Domain Name with Route53 & ACM
- **FQDN Parameter**: Pass your domain (e.g., `bitwarden.example.com`) as CDK parameter
- **Hosted Zone Lookup**: CDK automatically finds your existing Route53 hosted zone
- **ACM Certificate Lookup**: CDK finds existing certificate matching your FQDN or wildcard
- **DNS Record**: Lambda creates Alias record pointing to ALB (not IP)
- **DNS Cleanup**: Step Functions removes A record on shutdown (ALB remains)
- **Cost**: $0.50/month per hosted zone (if you don't already have one)

### ACM Certificate Requirements
Before deploying, create an ACM certificate in AWS Certificate Manager:
1. Go to ACM in AWS Console (must be in same region as deployment)
2. Request certificate for:
   - Specific: `bitwarden.example.com`, OR
   - Wildcard: `*.example.com`
3. Validate via DNS or email
4. CDK will automatically find and use it

### Lambda Functions in Python
All Lambda functions written in Python 3.11+ for:
- Better AWS SDK (boto3) integration
- Simpler error handling
- Faster cold starts than Node.js for AWS API calls
- Easier maintenance for infrastructure automation tasks

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
