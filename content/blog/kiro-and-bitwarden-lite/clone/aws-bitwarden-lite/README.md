# Bitwarden Lite on AWS - On-Demand Container Architecture

Cost-effective, secure Bitwarden Lite deployment on AWS using ECS Fargate with on-demand start/stop capabilities.

## Key Features

- **45-50% cost reduction** vs always-on VM (~$16-18/month vs $32/month)
- **API Gateway HTTP API** with custom domain and ACM certificate
- **Native Step Functions ECS integration** - no Lambda for status checks
- **Aurora Serverless v2 MySQL** - auto-scaling database
- **On-demand** - container only runs when you need it
- **Auto-shutdown** - configurable timeout (default 30 minutes)
- **Production-grade HTTPS** - ACM certificate with your domain

## Architecture

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

## Cost Breakdown (~$16-18/month)

- Fargate (2 hrs/day): ~$3/month
- Aurora Serverless v2: ~$4/month
- VPC Link: ~$7/month
- API Gateway HTTP API: <$0.10/month
- EFS, Lambda, Step Functions: ~$1/month
- Route53: $0.50/month

## Files

- `bitwarden-lite-aws-design.md` - Complete architecture documentation
- `lambda-start-container.py` - Start container Lambda (Python 3.13)
- `lambda-stop-container.py` - Stop container Lambda (Python 3.13)
- `lambda-cleanup.py` - Cleanup Lambda (Python 3.13)
- `step-functions-definition.json` - State machine with native ECS integration
- `requirements.txt` - Python dependencies

## Prerequisites

1. **ACM Certificate** (in us-east-1 for edge-optimized API Gateway):
   ```bash
   aws acm request-certificate \
     --domain-name bitwarden.example.com \
     --validation-method DNS \
     --region us-east-1
   ```

2. **Route53 Hosted Zone** for your domain

3. **AWS CDK** installed:
   ```bash
   npm install -g aws-cdk
   ```

## Quick Start

1. **Configure parameters** in `cdk.json`:
   ```json
   {
     "bitwardenFqdn": "bitwarden.example.com",
     "hostedZoneName": "example.com",
     "autoShutdownMinutes": 30
   }
   ```

2. **Deploy**:
   ```bash
   cdk deploy
   ```

3. **Start Bitwarden**:
   ```bash
   ./bitwarden-start.sh
   ```

4. **Access**: https://bitwarden.example.com

5. **Stop** (or wait for auto-shutdown):
   ```bash
   ./bitwarden-stop.sh
   ```

## Key Improvements

### vs ALB Architecture
- **50% cheaper**: VPC Link (~$7/month) vs ALB (~$17/month)
- **Simpler**: API Gateway HTTP API is easier to configure
- **Same security**: ACM certificate, private subnets, VPC isolation

### vs Original VM
- **45-50% cost reduction**
- **On-demand**: Only pay when running
- **Auto-scaling database**: Aurora Serverless v2
- **Better backups**: Automated Aurora snapshots
- **Infrastructure as Code**: CDK TypeScript

## Security

- Container in private subnet (no direct internet access)
- Database in private subnet
- HTTPS with ACM certificate
- Encryption at rest (Aurora, EFS)
- Secrets Manager for credentials
- VPC isolation

## Next Steps

See `bitwarden-lite-aws-design.md` for complete documentation including:
- Detailed architecture diagrams
- CDK construct implementation guide
- Step Functions workflow details
- Migration guide
- Troubleshooting

## License

MIT
