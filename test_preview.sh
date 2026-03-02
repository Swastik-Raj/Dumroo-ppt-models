#!/bin/bash

echo "Testing /api/generate/preview endpoint..."
echo ""

curl -X POST http://localhost:8000/api/generate/preview \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Introduction to Python Programming",
    "slide_count": 5,
    "theme": "Modern Minimal"
  }' \
  2>/dev/null | python3 -m json.tool | head -50

echo ""
echo "Check the Python server logs for [DEBUG] messages"
