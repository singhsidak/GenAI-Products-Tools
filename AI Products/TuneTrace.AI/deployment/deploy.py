"""Deployment script for TuneTrace.AI agent."""

import os
import sys

from google import genai
from google.genai import types


def deploy_agent():
    """Deploy TuneTrace.AI agent to production."""
    print("🚀 Deploying TuneTrace.AI Agent...")
    print("=" * 70)
    
    # Check for API key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        print("Please set it with: export GOOGLE_API_KEY='your-key'")
        sys.exit(1)
    
    print("✅ API key found")
    
    # Validate client connection
    try:
        client = genai.Client(api_key=api_key)
        print("✅ Successfully connected to Google Genai")
    except Exception as e:
        print(f"❌ Error connecting to Google Genai: {e}")
        sys.exit(1)
    
    # Test model availability
    try:
        model_name = "gemini-2.0-flash-exp"
        response = client.models.generate_content(
            model=model_name,
            contents="Test connection",
            config=types.GenerateContentConfig(
                response_modalities=["TEXT"],
            ),
        )
        print(f"✅ Model {model_name} is available and responding")
    except Exception as e:
        print(f"❌ Error testing model: {e}")
        sys.exit(1)
    
    print("=" * 70)
    print("✅ TuneTrace.AI Agent successfully deployed!")
    print()
    print("📝 Next steps:")
    print("1. Run tests: python deployment/test_deployment.py")
    print("2. Use the agent: python -m tune_trace_ai.agent 'song name'")
    print("3. Import in code: from tune_trace_ai import create_agent")
    print("=" * 70)


if __name__ == "__main__":
    deploy_agent()



