# Files Overview

Complete list of all files in this directory with descriptions.

## 📖 Documentation (8 files)

### 1. **INDEX.md** ⭐ START HERE
Overview of all files and where to start based on your needs.

### 2. **README.md**
Quick start guide with architecture overview, cost breakdown, and key features.

### 3. **bitwarden-lite-aws-design.md** (Comprehensive - ~700 lines)
Complete architecture documentation including:
- Detailed architecture diagrams
- All components explained
- CDK implementation guide
- Security features
- Step Functions workflow
- Migration guide

### 4. **CHANGES_SUMMARY.md**
Explains the three major improvements:
- API Gateway HTTP API instead of ALB
- Native Step Functions ECS integration
- Cost comparisons and technical details

### 5. **QUICK_REFERENCE.md**
Cheat sheet with:
- Quick commands
- Environment variables
- Troubleshooting tips
- Useful AWS CLI commands

### 6. **DEPLOYMENT_GUIDE.md**
Step-by-step deployment instructions:
- Prerequisites
- ACM certificate creation
- CDK project setup
- Deployment steps
- Verification
- Troubleshooting

### 7. **CHECKLIST.md**
Comprehensive deployment checklist:
- Pre-deployment tasks
- CDK setup
- Deployment steps
- Testing procedures
- Post-deployment configuration
- Security hardening

### 8. **FILES_OVERVIEW.md** (This file)
Overview of all files in the directory.

## 💻 Lambda Functions (3 files - Python 3.13)

### 9. **lambda-start-container.py** (~200 lines)
Starts ECS Fargate task, updates Route53 DNS, triggers Step Functions.

**Environment Variables:**
- CLUSTER_NAME
- TASK_DEFINITION
- SUBNET_IDS
- CONTAINER_SECURITY_GROUP_ID
- STATE_MACHINE_ARN
- API_GATEWAY_DOMAIN_NAME
- API_GATEWAY_HOSTED_ZONE_ID
- HOSTED_ZONE_ID
- FQDN
- AUTO_SHUTDOWN_MINUTES

### 10. **lambda-stop-container.py** (~150 lines)
Stops ECS task, removes DNS record, cancels Step Functions execution.

**Environment Variables:**
- CLUSTER_NAME
- API_GATEWAY_DOMAIN_NAME
- API_GATEWAY_HOSTED_ZONE_ID
- HOSTED_ZONE_ID
- FQDN

### 11. **lambda-cleanup.py** (~100 lines)
Cleanup resources after auto-shutdown (called by Step Functions).
Removes DNS record.

**No environment variables** - all passed via event.

## 🔧 Infrastructure (1 file)

### 12. **step-functions-definition.json**
State machine definition with native ECS integration.

**States:**
1. WaitForTimeout (30 minutes)
2. DescribeTask (native ECS integration)
3. CheckTaskStatus (choice state)
4. StopTask (native ECS integration)
5. CleanupResources (Lambda)
6. AlreadyStopped (success)

## 🚀 Shell Scripts (2 files)

### 13. **bitwarden-start.sh**
Starts Bitwarden container via Control API Gateway.

**Configuration needed:**
- CONTROL_API_URL
- API_KEY

**Features:**
- Gets current public IP
- Calls Control API
- Displays HTTPS URL
- Optional browser opening

### 14. **bitwarden-stop.sh**
Stops Bitwarden container via Control API Gateway.

**Configuration needed:**
- CONTROL_API_URL
- API_KEY

**Features:**
- Calls Control API
- Confirms shutdown
- Displays cleanup status

## ⚙️ Configuration Examples (4 files)

### 15. **cdk.json.example**
CDK configuration with context parameters.

**Key parameters:**
- bitwardenFqdn: "bitwarden.example.com"
- hostedZoneName: "example.com"
- autoShutdownMinutes: 30
- enableSpot: false
- auroraMinCapacity: 0.5
- auroraMaxCapacity: 1

### 16. **package.json.example**
NPM package configuration for CDK project.

**Key dependencies:**
- aws-cdk-lib: 2.114.0
- constructs: ^10.0.0
- typescript: ~5.3.0

### 17. **tsconfig.json.example**
TypeScript compiler configuration.

### 18. **requirements.txt**
Python dependencies for Lambda functions.

**Dependencies:**
- boto3>=1.35.0
- botocore>=1.35.0

## 🔒 Other (1 file)

### 19. **.gitignore**
Git ignore file for CDK project.

**Ignores:**
- CDK output (cdk.out/)
- Node modules
- Python cache
- IDE files
- Secrets
- OS files

---

## Total: 19 Files

### By Category:
- **Documentation**: 8 files
- **Lambda Functions**: 3 files
- **Infrastructure**: 1 file
- **Shell Scripts**: 2 files
- **Configuration**: 4 files
- **Other**: 1 file

### By File Type:
- **Markdown (.md)**: 8 files
- **Python (.py)**: 3 files
- **Shell (.sh)**: 2 files
- **JSON**: 3 files
- **Other**: 3 files

---

## Quick Navigation

### I want to...

**Understand the architecture**
→ README.md → bitwarden-lite-aws-design.md

**See what changed from original design**
→ CHANGES_SUMMARY.md

**Deploy the solution**
→ DEPLOYMENT_GUIDE.md → CHECKLIST.md

**Get quick reference**
→ QUICK_REFERENCE.md

**Find a specific file**
→ INDEX.md

**Start coding**
→ Lambda functions (.py files) → step-functions-definition.json

**Configure CDK**
→ cdk.json.example → package.json.example → tsconfig.json.example

**Use shell scripts**
→ bitwarden-start.sh → bitwarden-stop.sh

---

## File Sizes (Approximate)

| File | Lines | Size |
|------|-------|------|
| bitwarden-lite-aws-design.md | ~700 | Large |
| DEPLOYMENT_GUIDE.md | ~400 | Large |
| CHECKLIST.md | ~350 | Large |
| CHANGES_SUMMARY.md | ~300 | Medium |
| lambda-start-container.py | ~200 | Medium |
| QUICK_REFERENCE.md | ~200 | Medium |
| README.md | ~150 | Medium |
| lambda-stop-container.py | ~150 | Medium |
| INDEX.md | ~150 | Medium |
| lambda-cleanup.py | ~100 | Small |
| step-functions-definition.json | ~80 | Small |
| bitwarden-start.sh | ~60 | Small |
| bitwarden-stop.sh | ~40 | Small |
| cdk.json.example | ~100 | Small |
| package.json.example | ~40 | Small |
| tsconfig.json.example | ~30 | Small |
| requirements.txt | ~10 | Tiny |
| .gitignore | ~30 | Tiny |

---

## Reading Order

### For Quick Start:
1. INDEX.md (5 min)
2. README.md (10 min)
3. QUICK_REFERENCE.md (10 min)
4. DEPLOYMENT_GUIDE.md (30 min)

### For Complete Understanding:
1. INDEX.md (5 min)
2. README.md (10 min)
3. CHANGES_SUMMARY.md (15 min)
4. bitwarden-lite-aws-design.md (60 min)
5. DEPLOYMENT_GUIDE.md (30 min)
6. CHECKLIST.md (20 min)

### For Implementation:
1. DEPLOYMENT_GUIDE.md (30 min)
2. CHECKLIST.md (20 min)
3. Lambda functions (30 min)
4. step-functions-definition.json (10 min)
5. Configuration examples (10 min)
6. Shell scripts (10 min)

---

## Next Steps

1. ✅ Read INDEX.md
2. ✅ Read README.md
3. ⏳ Create ACM certificate
4. ⏳ Follow DEPLOYMENT_GUIDE.md
5. ⏳ Use CHECKLIST.md to track progress
6. ⏳ Deploy and test

---

**All files are ready!** Start with INDEX.md or README.md.
