#!/bin/bash

# Test backend status
echo "Testing backend at: https://web-production-4ae9.up.railway.app"
echo ""

echo "1. Testing root endpoint..."
curl -s https://web-production-4ae9.up.railway.app/ | jq . || echo "❌ Root endpoint failed"

echo ""
echo "2. Testing health endpoint..."
curl -s https://web-production-4ae9.up.railway.app/health | jq . || echo "❌ Health endpoint failed"

echo ""
echo "3. Testing API health endpoint..."
curl -s https://web-production-4ae9.up.railway.app/api/health | jq . || echo "❌ API health endpoint failed"

echo ""
echo "4. Testing text processing..."
curl -s -X POST https://web-production-4ae9.up.railway.app/api/text \
  -H "Content-Type: application/json" \
  -d '{"text": "create a blue cube"}' | jq . || echo "❌ Text processing failed"
