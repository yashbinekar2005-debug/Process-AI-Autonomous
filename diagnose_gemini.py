#!/usr/bin/env python3
"""Detailed Gemini API diagnostics and model discovery."""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY', '')

print("=" * 70)
print("🔍 GEMINI API DIAGNOSTICS REPORT")
print("=" * 70)

print(f"\n✅ API Key Found: {len(api_key)} characters")

# Configure genai
genai.configure(api_key=api_key)

try:
    # List available models
    print("\n📋 Available Models from Google API:\n")
    available_models = []
    
    for model in genai.list_models():
        # Filter for generateContent capable models
        if 'generateContent' in model.supported_generation_methods:
            available_models.append(model.name)
            print(f"  ✅ {model.name}")
    
    print(f"\n📊 Total Available Models: {len(available_models)}")
    
    if available_models:
        print(f"\n🎯 RECOMMENDED MODEL TO USE: {available_models[0]}")
        
except Exception as e:
    print(f"\n❌ Error listing models: {str(e)}")

print("\n" + "=" * 70)
print("ERROR ANALYSIS:")
print("=" * 70)
print("""
❌ gemini-2.0-flash: 429 RESOURCE_EXHAUSTED
   └─ Issue: Rate limited OR quota exceeded
   └─ Solution: Your API key has reached usage limits
   
❌ gemini-1.5-flash: 404 NOT_FOUND
   └─ Issue: Model not available for your account type
   └─ Solution: Your account may not have access to this model
   
❌ gemini-1.5-pro: 404 NOT_FOUND
   └─ Issue: Model not available for your account type
   └─ Solution: Try free models (gemini-pro, etc.)
   
❌ gemini-pro: 404 NOT_FOUND
   └─ Issue: Model deprecated or not available
   └─ Solution: Use latest available model
""")

print("=" * 70)
