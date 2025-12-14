# Bitwarden Lite on AWS - Container-Based On-Demand Architecture (CDK TypeScript)

## Overview

This design replaces the VM-based Bitwarden deployment with a containerized Bitwarden Lite solution that runs only when needed, significantly reducing costs while maintaining security. Built with AWS CDK using TypeScript for infrastructure as code.

**Key Innovation**: Uses API Gateway HTTP API with custom domain instead of Application Load Balancer, reducing costs by 50% while maintaining production-grade HTTPS.

## Architecture Components

### 1. Container Infrastructure
- **AWS ECS Fargate** - Serverless container platform (no VM management)
- **Bitwarden Lite Container** - MySQL-based version (HTTP only, API Gateway handles HTTPS)
- **Aurora Serverless v2 MySQL** - Scalable, pay-per-use database that auto-scales to zero
- **VPC Link** - Connects API Gateway to private ECS tasks

### 2. On-Demand Control
- **Lambda Function** - Starts the ECS task and triggers Step Functions
- **Step Functions** - Orchestrates auto-shutdown workflow with **native ECS integration**
- **Control API Gateway (REST)** - Endpoint for triggering Lambda
- **Shell Script** - Local script to start container and access Bitwarden

### 3. HTTPS Access Layer
- **API Gateway HTTP API** - Custom domain with ACM certificate for Bitwarden access
- **VPC Link** - Private integration to ECS tasks
- **Route53** - DNS management for custom domain

### 4. Security Layers
- **Security Group** - Restricts VPC Link access to container only
- **VPC** - Private networking with private subnets for container
- **ACM Certificate** - Automatic HTTPS with your domain (you provide the certificate)
- **Secrets Manager** - Stores database credentials, Bitwarden config, and API keys
- **IAM Roles** - Least privilege access for all components

### 5. Cost Optimization
- **Step Functions with native ECS integration** - No Lambda for status checks
- **Aurora Serverless v2** - Scales to 0.5 ACU when idle
- **API Gateway HTTP API** - Much cheaper than ALB (~$7/month vs ~$17/month)
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
         │ 1. Trigger start
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         AWS Cloud                                    │
│                                                                      │
│  ┌──────────────────┐      ┌──────────────────────────────────┐    │
│  │ Control API      │─────▶│  Lambda (Start Function)         │    │
│  │ Gateway (REST)   │      │  - Start ECS Task                │    │
│  └──────────────────┘      │  - Update Route53                │    │
│                            │  - Trigger Step Functions        │    │
│                            │  - Return HTTPS endpoint         │    │
│                            └──────────┬───────────────────────┘    │
│                                       │                             │
│                                       ▼                             │
│                            ┌──────────────────────────────────┐    │
│                            │  Step Functions Workflow         │    │
│                            │  1. Wait (30 min)                │    │
│                            │  2. ECS:DescribeTasks (native)   │    │
│                            │  3. ECS:StopTask (native)        │    │
│                            │  4. Lambda: Cleanup DNS          │    │
│                            └──────────────────────────────────┘    │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  API Gateway HTTP API (Bitwarden Access)                 │      │
│  │  - Custom Domain: bitwarden.example.com                  │      │
│  │  - ACM Certificate (HTTPS)                               │      │
│  │  - VPC Link to private ECS tasks                         │      │
│  │  - Route: /* → VPC Link → Container:8080                 │      │
│  └──────────────────┬───────────────────────────────────────┘      │
│                     │                                               │
│                     ▼                                               │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  VPC Link (NLB in private subnets)                       │      │
│  │  - Connects API Gateway to private resources             │      │
│  │  - Forwards to ECS Service                               │      │
│  └──────────────────┬───────────────────────────────────────┘      │
│                     │                                               │
│                     ▼                                               │
│  ┌───────────────────────────────────────────────────┐             │
│  │           ECS Fargate Cluster                     │             │
│  │                                                   │             │
│  │  ┌─────────────────────────────────────────┐    │             │
│  │  │  Bitwarden Lite Container               │    │             │
│  │  │  - Port 8080 (HTTP only)                │    │             │
│  │  │  - API Gateway handles HTTPS            │    │             │
│  │  │  - Connects to Aurora MySQL             │    │             │
│  │  │  - EFS for attachments/config           │    │             │
│  │  └──────────────┬──────────────────────────┘    │             │
│  └─────────────────┼───────────────────────────────┘             │
│                    │                                               │
│         ┌──────────┴──────────┐                                   │
│         ▼                     ▼                                   │
│  ┌──────────────┐    ┌─────────────────────────┐                │
│  │     EFS      │    │  Aurora Serverless v2   │                │
│  │ - attachments│    │  MySQL Database         │                │
│  │ - config     │    │  - Auto-scales          │                │
│  │ - logs       │    │  - Min: 0.5 ACU         │                │
│  └──────────────┘    │  - Max: 1 ACU           │                │
│                      └─────────────────────────┘                │
│                                                                  │
│  ┌────────────────────────────────┐                             │
│  │  Security Groups               │                             │
│  │  Container SG:                 │                             │
│  │  - Ingress: VPC Link only      │                             │
│  │  - Port 8080 (HTTP)            │                             │
│  │                                │                             │
│  │  Database SG:                  │                             │
│  │  - Ingress: Container SG only  │                             │
│  │  - Port 3306 (MySQL)           │                             │
│  └────────────────────────────────┘                             │
│                                                                  │
│  ┌────────────────────────────────┐                             │
│  │  Route53                       │                             │
│  │  A Record: bitwarden.example.  │                             │
│  │  com → API Gateway domain      │                             │
│  │  (Alias)                       │                             │
│  └────────────────────────────────┘                             │
│                                                                  │
│  ┌────────────────────────────────┐                             │
│  │  ACM Certificate               │                             │
│  │  (You provide)                 │                             │
│  │  - *.example.com or            │                             │
│  │  - bitwarden.example.com       │                             │
│  │  - Must be in us-east-1        │                             │
│  └────────────────────────────────┘                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Workflow

### Starting Bitwarden
1. Run local shell script: `./bitwarden-start.sh`
2. Script calls Control API Gateway with authentication token
3. Lambda function (Start):
   - Starts ECS Fargate task in private subnet
   - Updates Route53 A record to point to API Gateway custom domain
   - Triggers Step Functions workflow for auto-shutdown
   - Waits for task to be healthy
   - Returns the HTTPS endpoint URL
4. Script displays URL: `https://bitwarden.example.com`
5. Access your passwords via browser or CLI

### Auto-Shutdown (Step Functions with Native ECS Integration)
1. Step Functions workflow starts when container launches
2. **Wait State**: Pauses for configurable duration (default 30 minutes)
3. **ECS DescribeTasks State**: Native ECS integration checks task status (no Lambda!)
4. **Choice State**: Determines if task is still running
5. **ECS StopTask State**: Native ECS integration stops task (no Lambda!)
6. **Cleanup Lambda**: Removes Route53 record
7. Aurora database auto-scales down to minimum
8. Billing stops for compute resources

### Manual Shutdown
- Run: `./bitwarden-stop.sh`
- Calls Control API Gateway stop endpoint
- Lambda cancels the Step Functions execution
- Stops the ECS task immediately
- Cleans up Route53 record

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
- **VPC Link**: $0.01/hour = ~$7.20/month (always running)
- **API Gateway HTTP API**: $1.00/million requests
  - ~1,000 requests/month: ~$0.001/month (negligible)
  - Custom domain: $0/month (included)
  - **Subtotal**: <$0.10/month
- **EFS Storage** (2GB for attachments): ~$0.60/month
- **Lambda**: <$0.20/month (free tier covers most usage)
- **Control API Gateway (REST)**: <$0.10/month (free tier covers most usage)
- **Step Functions**: <$0.10/month (4,000 free state transitions/month)
- **Route53**: $0.50/month (if new hosted zone)
- **Total**: ~$16-18/month (45-50% cost reduction)

**Note**: VPC Link adds ~$7/month but is much cheaper than ALB (~$17/month). API Gateway HTTP API with custom domain provides production-grade HTTPS with ACM certificate at minimal cost.

### Cost Comparison: API Gateway vs ALB

| Component | ALB Architecture | API Gateway Architecture | Savings |
|-----------|------------------|-------------------------|---------|
| Load Balancer/VPC Link | ~$17/month | ~$7/month | $10/month |
| Request charges | Included in ALB | <$0.10/month | ~$0 |
| **Total difference** | | | **~$10/month (58% cheaper)** |

## Security Features

### 1. Network Isolation
- Container runs in private subnet (no direct internet access)
- Database in private subnet (no internet access)
- VPC Link provides secure connection from API Gateway
- Container Security Group only allows VPC Link access
- Database Security Group only allows container access

### 2. Authentication Layers
- Control API Gateway requires API key or IAM authentication
- Bitwarden requires master password
- Database credentials stored in Secrets Manager
- Optional: Add AWS Cognito for additional auth layer on Bitwarden access
- Optional: Add IP-based access control via API Gateway resource policy

### 3. Encryption
- Aurora encrypted at rest (AWS KMS)
- EFS encrypted at rest (AWS KMS)
- HTTPS/TLS via API Gateway with ACM certificate (you provide)
- Secrets Manager for database credentials and sensitive data
- TLS 1.2+ enforced on API Gateway

### 4. Audit Trail
- CloudWatch Logs for all Lambda invocations
- Step Functions execution history
- ECS task logs
- API Gateway access logs
- Aurora query logs (optional)
- CloudTrail for API calls

## Implementation Approach

### Selected Architecture
- **API Gateway HTTP API** with custom domain and ACM certificate (you provide)
- **HTTPS only** - API Gateway terminates SSL
- **Container in private subnet** - HTTP (8080) from VPC Link only
- **Aurora Serverless v2 MySQL** in private subnet
- **Step Functions with native ECS integration** - No Lambda for status checks
- **CDK TypeScript** for infrastructure as code
- **Route53** for DNS management

### Why This Architecture
- **Cost-effective**: API Gateway HTTP API + VPC Link (~$7/month) vs ALB (~$17/month)
- **Production-grade HTTPS**: ACM certificate with proper SSL/TLS
- **Secure**: Container not directly exposed to internet
- **Professional**: Access via domain name
- **Flexible**: Works with wildcard or specific certificates
- **Simplified**: Native Step Functions ECS integration, fewer Lambda functions
- **Scalable**: API Gateway handles traffic spikes automatically

### ACM Certificate Handling
- **You provide**: Create ACM certificate for your domain beforehand
- **CDK discovers**: Looks up existing certificate by domain name
- **Supports**: Both wildcard (*.example.com) and specific (bitwarden.example.com)
- **No creation**: CDK won't create certificate (you manage validation)
- **Region**: Must be in **us-east-1** for edge-optimized API Gateway custom domains

## Bitwarden Lite Specifics

### Container Configuration
```dockerfile
# Bitwarden Lite HTTP only (API Gateway handles HTTPS)
# Port 8080: HTTP
# Uses MySQL database (Aurora Serverless v2)
# Minimal resource requirements: 0.5 vCPU, 1GB RAM
```

### Environment Variables
```bash
BW_DOMAIN=bitwarden.example.com
BW_HTTP_PORT=8080
# No HTTPS port needed - API Gateway handles HTTPS termination

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

# No SSL configuration needed - API Gateway handles certificate
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
# - Call Control API Gateway to start container
# - Poll for container readiness
# - Display HTTPS URL
# - Optional: Open browser automatically
# - Show estimated auto-shutdown time
```

Example output:
```
Starting Bitwarden container...
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
# - Call Control API Gateway to stop container
# - Cancel Step Functions execution
# - Confirm shutdown
# - Display cost savings message
```

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
│   │   ├── container.ts          # ECS Fargate task + service
│   │   ├── api-gateway.ts        # HTTP API with custom domain + VPC Link
│   │   ├── control-api.ts        # REST API for start/stop control
│   │   ├── dns.ts                # Route53 record management
│   │   └── orchestration.ts     # Step Functions with native ECS
│   └── lambda/
│       ├── start-container/      # Start Lambda handler (Python 3.13)
│       │   ├── index.py
│       │   └── requirements.txt
│       ├── stop-container/       # Stop Lambda handler (Python 3.13)
│       │   ├── index.py
│       │   └── requirements.txt
│       └── cleanup/              # Cleanup Lambda (Python 3.13)
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
   - VPC with private subnets
   - Security groups (container, database, VPC Link)
   - NAT Gateway (for container to reach AWS services)

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
   - Task definition (port 8080)
   - ECS Service for VPC Link integration
   - IAM roles

5. **API Gateway Construct** (`api-gateway.ts`)
   - HTTP API with custom domain
   - ACM certificate lookup (us-east-1)
   - VPC Link to ECS Service
   - Route53 A record (Alias to API Gateway)
   - Integration with ECS Service

6. **Control API Construct** (`control-api.ts`)
   - REST API Gateway for start/stop
   - Lambda functions (start, stop)
   - API key for authentication

7. **DNS Construct** (`dns.ts`)
   - Route53 hosted zone lookup
   - A record management

8. **Orchestration Construct** (`orchestration.ts`)
   - Step Functions state machine
   - Native ECS integration (DescribeTasks, StopTask)
   - Cleanup Lambda (Python 3.13)

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
// Certificate MUST be in us-east-1 for edge-optimized API Gateway
const certificateRegion = 'us-east-1';

// 1. First, try to find exact match for FQDN
const exactCert = Certificate.fromLookup(scope, 'ExactCert', {
  domainName: 'bitwarden.example.com',
  region: certificateRegion
});

// 2. If not found, try wildcard certificate
const wildcardCert = Certificate.fromLookup(scope, 'WildcardCert', {
  domainName: '*.example.com',
  region: certificateRegion
});

// 3. Use whichever is found (exact match preferred)
```

**Supported certificate patterns:**
- Exact match: `bitwarden.example.com`
- Wildcard: `*.example.com`
- Multi-domain: Certificate with both domains

**Important**: For API Gateway HTTP API custom domains, certificate must be in **us-east-1** region (for edge-optimized endpoints).

## Step Functions Workflow with Native ECS Integration

### State Machine Definition
```json
{
  "Comment": "Auto-shutdown workflow for Bitwarden container with native ECS integration",
  "StartAt": "WaitForTimeout",
  "States": {
    "WaitForTimeout": {
      "Type": "Wait",
      "Seconds": 1800,
      "Next": "DescribeTask"
    },
    "DescribeTask": {
      "Type": "Task",
      "Resource": "arn:aws:states:::ecs:describeTasks",
      "Parameters": {
        "Cluster": "${ClusterArn}",
        "Tasks.$": "States.Array($.taskArn)"
      },
      "ResultPath": "$.describeResult",
      "Next": "CheckTaskStatus",
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "AlreadyStopped"
        }
      ]
    },
    "CheckTaskStatus": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.describeResult.Tasks[0].LastStatus",
          "StringEquals": "RUNNING",
          "Next": "StopTask"
        }
      ],
      "Default": "AlreadyStopped"
    },
    "StopTask": {
      "Type": "Task",
      "Resource": "arn:aws:states:::ecs:stopTask",
      "Parameters": {
        "Cluster": "${ClusterArn}",
        "Task.$": "$.taskArn",
        "Reason": "Auto-shutdown after timeout"
      },
      "ResultPath": "$.stopResult",
      "Next": "CleanupResources",
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "CleanupResources"
        }
      ]
    },
    "CleanupResources": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${CleanupLambdaArn}",
        "Payload": {
          "taskArn.$": "$.taskArn",
          "hostedZoneId.$": "$.hostedZoneId",
          "fqdn.$": "$.fqdn"
        }
      },
      "End": true
    },
    "AlreadyStopped": {
      "Type": "Succeed"
    }
  }
}
```

### Benefits of Native ECS Integration
- **No Lambda needed**: Step Functions directly calls ECS APIs
- **Simpler**: Fewer moving parts, less code to maintain
- **Cheaper**: No Lambda invocations for status checks
- **More reliable**: Direct AWS service integration
- **Better visibility**: See ECS API calls in Step Functions execution history
- **Error handling**: Built-in retry and error handling

## Migration from VM

### Prerequisites
1. **Create ACM Certificate** (in us-east-1):
   ```bash
   aws acm request-certificate \
     --domain-name bitwarden.example.com \
     --validation-method DNS \
     --region us-east-1
   ```
   
   Or use wildcard:
   ```bash
   aws acm request-certificate \
     --domain-name "*.example.com" \
     --validation-method DNS \
     --region us-east-1
   ```

2. **Validate Certificate**:
   - Add CNAME record to Route53 for DNS validation
   - Wait for certificate status to be "Issued"

3. **Verify Route53 Hosted Zone**:
   ```bash
   aws route53 list-hosted-zones
   ```

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

## Next Steps

1. **Initialize CDK Project**
   ```bash
   mkdir bitwarden-cdk && cd bitwarden-cdk
   cdk init app --language typescript
   npm install aws-cdk-lib constructs
   ```

2. **Create CDK Constructs** (in order)
   - Network construct (VPC, subnets, security groups)
   - Database construct (Aurora Serverless v2)
   - Storage construct (EFS)
   - Container construct (ECS Fargate with Service)
   - API Gateway construct (HTTP API + custom domain + VPC Link)
   - Control API construct (REST API for start/stop)
   - DNS construct (Route53 record management)
   - Orchestration construct (Step Functions with native ECS)

3. **Implement Lambda Functions** (Python 3.13)
   - Start container handler
   - Stop container handler
   - Cleanup handler (DNS removal)

4. **Create Step Functions Workflow**
   - Wait state (30 minutes)
   - Native ECS DescribeTasks
   - Native ECS StopTask
   - Cleanup Lambda

5. **Create Shell Scripts**
   - bitwarden-start.sh
   - bitwarden-stop.sh

6. **Deploy and Test**
   ```bash
   cdk synth    # Validate CloudFormation
   cdk deploy   # Deploy to AWS
   ```

## Estimated Implementation Time

- **CDK Infrastructure**: 6-8 hours
- **Lambda Functions**: 2-3 hours (fewer functions needed)
- **Step Functions Workflow**: 1-2 hours (native ECS integration)
- **Container Configuration**: 2-3 hours
- **Shell Scripts**: 1-2 hours
- **Testing**: 2-3 hours
- **Total**: 14-21 hours (2-3 days of focused work)

## Additional Considerations

### VPC Link Considerations
- VPC Link creates a Network Load Balancer in your VPC
- Always running (~$7/month base cost)
- Provides secure connection from API Gateway to private resources
- Supports multiple integrations (can be reused for other services)
- Automatically handles health checks

### API Gateway HTTP API vs REST API
- **HTTP API**: Cheaper, simpler, better for proxying to backends
- **REST API**: More features (resource policies, usage plans, etc.)
- We use HTTP API for Bitwarden access (cost-effective)
- We use REST API for control plane (more security features)

### API Gateway Custom Domain
- Requires ACM certificate in us-east-1 (for edge-optimized)
- Automatically creates CloudFront distribution
- Global edge locations for low latency
- Automatic DDoS protection via AWS Shield

### Session Management
- Keep browser session alive to avoid re-authentication
- Use Bitwarden browser extension with self-hosted server
- Configure session timeout in Bitwarden settings
- Consider longer timeout since container auto-stops anyway

### Monitoring & Alerts

#### CloudWatch Metrics
- ECS task CPU/Memory utilization
- Container start/stop events
- Lambda execution duration and errors
- API Gateway request count and latency
- Step Functions execution status

#### Optional Alerts
- SNS notification when container starts
- Alert if container runs >4 hours (cost control)
- Alert on failed starts
- Alert on API Gateway 5xx errors

### Backup Strategy

#### Automated Backups
- **Aurora Automated Backups**: Daily snapshots, 7-day retention (included)
- **Aurora Continuous Backup**: Point-in-time recovery (optional)
- **AWS Backup for EFS**: Daily snapshots for attachments
- Retention: 7 days
- Cost: ~$0.05/GB/month for EFS backups

#### Manual Export
- Script to export Bitwarden vault to JSON
- Store encrypted backup in S3
- Lifecycle policy to Glacier after 30 days
- Lambda function for scheduled exports (optional)

## Conclusion

This architecture provides a cost-effective, secure, and convenient way to run Bitwarden Lite on AWS with the following improvements:

✅ **API Gateway HTTP API** instead of ALB (58% cheaper: ~$7/month vs ~$17/month)
✅ **Native Step Functions ECS integration** (no Lambda for status checks)
✅ **Aurora Serverless v2 MySQL** for better reliability and backups
✅ **CDK TypeScript** for type-safe infrastructure as code
✅ **Production-grade HTTPS** with ACM certificate
✅ **45-50% cost reduction** vs VM (~$16-18/month vs $32/month)

The on-demand nature means you only pay for what you use, while maintaining strong security through VPC isolation, encryption, and proper HTTPS.
