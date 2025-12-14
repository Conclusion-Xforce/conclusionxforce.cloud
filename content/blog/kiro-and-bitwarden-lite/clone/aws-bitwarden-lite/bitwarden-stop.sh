#!/bin/bash
#
# Bitwarden Stop Script
# Stops the Bitwarden container via AWS API Gateway
#

set -e

# Configuration - Update these values after CDK deployment
CONTROL_API_URL="https://YOUR_CONTROL_API_ID.execute-api.YOUR_REGION.amazonaws.com/prod/stop"
API_KEY="YOUR_API_KEY"  # Get from CDK output or AWS Console

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Stopping Bitwarden container..."

# Get current public IP (optional - for logging)
PUBLIC_IP=$(curl -s https://api.ipify.org)

# Call Control API to stop container
echo "Requesting container stop..."
RESPONSE=$(curl -s -X POST "$CONTROL_API_URL" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"sourceIp\": \"$PUBLIC_IP\"}")

# Check if request was successful
if echo "$RESPONSE" | grep -q "error"; then
  echo "Error stopping container:"
  echo "$RESPONSE" | jq '.'
  exit 1
fi

echo ""
echo -e "${GREEN}✓ Container stopped successfully!${NC}"
echo ""
echo "Resources cleaned up:"
echo "  - ECS task stopped"
echo "  - DNS record removed"
echo "  - Step Functions execution canceled"
echo ""
echo -e "${YELLOW}Cost savings: Container is no longer running${NC}"
echo ""
