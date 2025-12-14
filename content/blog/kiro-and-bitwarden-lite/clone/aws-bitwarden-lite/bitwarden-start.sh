#!/bin/bash
#
# Bitwarden Start Script
# Starts the Bitwarden container via AWS API Gateway
#

set -e

# Configuration - Update these values after CDK deployment
CONTROL_API_URL="https://YOUR_CONTROL_API_ID.execute-api.YOUR_REGION.amazonaws.com/prod/start"
API_KEY="YOUR_API_KEY"  # Get from CDK output or AWS Console

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Starting Bitwarden container..."

# Get current public IP (optional - for logging)
PUBLIC_IP=$(curl -s https://api.ipify.org)
echo "Your IP: $PUBLIC_IP"

# Call Control API to start container
echo "Requesting container start..."
RESPONSE=$(curl -s -X POST "$CONTROL_API_URL" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"sourceIp\": \"$PUBLIC_IP\"}")

# Check if request was successful
if echo "$RESPONSE" | grep -q "error"; then
  echo "Error starting container:"
  echo "$RESPONSE" | jq '.'
  exit 1
fi

# Extract URL from response
BITWARDEN_URL=$(echo "$RESPONSE" | jq -r '.body' | jq -r '.url')
AUTO_SHUTDOWN=$(echo "$RESPONSE" | jq -r '.body' | jq -r '.autoShutdownMinutes')

echo ""
echo -e "${GREEN}✓ Container is starting!${NC}"
echo ""
echo "Container starting... (this may take 30-60 seconds)"
echo "Updating DNS record..."
echo ""

# Wait a bit for DNS propagation
sleep 10

echo -e "${GREEN}✓ Container is ready!${NC}"
echo ""
echo "Access Bitwarden at: ${GREEN}$BITWARDEN_URL${NC}"
echo ""
echo -e "${YELLOW}Note: DNS propagation may take 30-60 seconds.${NC}"
echo "Auto-shutdown in $AUTO_SHUTDOWN minutes."
echo "To stop manually, run: ./bitwarden-stop.sh"
echo ""

# Optional: Open browser
read -p "Open browser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  if command -v xdg-open &> /dev/null; then
    xdg-open "$BITWARDEN_URL"
  elif command -v open &> /dev/null; then
    open "$BITWARDEN_URL"
  else
    echo "Please open $BITWARDEN_URL in your browser"
  fi
fi
