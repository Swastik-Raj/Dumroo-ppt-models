#!/usr/bin/env python3
"""Test script to verify the API endpoints."""
import json
import os
import sys

def test_preview_endpoint():
    """Test the preview generation endpoint."""
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)

    # Test data
    request_data = {
        "topic": "Introduction to Python Programming",
        "slide_count": 5,
        "theme": "Modern Minimal"
    }

    print("Testing /api/generate/preview endpoint...")
    print(f"Request: {json.dumps(request_data, indent=2)}")

    response = client.post("/api/generate/preview", json=request_data)

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nResponse Preview:")
        print(f"  Presentation ID: {data.get('presentation_id')}")
        print(f"  Topic: {data.get('topic')}")
        print(f"  Theme: {data.get('theme')}")
        print(f"  Slides Count: {len(data.get('slides', []))}")
        print(f"\nSlide Details:")
        for i, slide in enumerate(data.get('slides', [])[:3], 1):
            print(f"\n  Slide {i}:")
            print(f"    Type: {slide.get('type')}")
            print(f"    Title: {slide.get('title')}")
            print(f"    Content: {slide.get('content')[:100]}...")
            print(f"    Keywords: {slide.get('keywords')}")

        return data.get('presentation_id')
    else:
        print(f"Error: {response.text}")
        return None

def test_download_endpoint(presentation_id):
    """Test the download endpoint."""
    from app.main import app
    from fastapi.testclient import TestClient

    if not presentation_id:
        print("\nSkipping download test - no presentation ID")
        return

    client = TestClient(app)

    print(f"\n\nTesting /api/presentation/{presentation_id}/download endpoint...")

    response = client.post(f"/api/presentation/{presentation_id}/download")

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content-Length: {len(response.content)} bytes")
        print(f"File downloaded successfully!")

        # Check if it's a valid PPTX (should start with PK signature)
        if response.content[:2] == b'PK':
            print("✓ Valid PPTX file signature detected")
        else:
            print("✗ Invalid PPTX file signature")
    else:
        print(f"Error: {response.text}")

def check_api_keys():
    """Check if API keys are configured."""
    print("Checking API Configuration...")
    from app.config import settings

    print(f"  AI Provider: {settings.ai_provider}")
    print(f"  OpenAI API Key: {'✓ Set' if settings.openai_api_key else '✗ Not Set'}")
    print(f"  Gemini API Key: {'✓ Set' if settings.gemini_api_key else '✗ Not Set'}")
    print(f"  Unsplash Access Key: {'✓ Set' if settings.unsplash_access_key else '✗ Not Set'}")

    if not settings.openai_api_key and not settings.gemini_api_key:
        print("\n⚠ WARNING: No AI API keys configured. Using mock fallback data.")

    print()

if __name__ == "__main__":
    check_api_keys()
    presentation_id = test_preview_endpoint()
    test_download_endpoint(presentation_id)
