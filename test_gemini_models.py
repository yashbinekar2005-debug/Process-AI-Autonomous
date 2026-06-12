#!/usr/bin/env python3
"""Test script to verify Gemini API key and available models."""

from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY', '')

print("🔑 API Key Status:", "✅ SET" if api_key else "❌ EMPTY")
print(f"🔐 Key Length: {len(api_key)} characters\n")

models_to_test = [
    'gemini-2.0-flash',
    'gemini-1.5-flash', 
    'gemini-1.5-pro',
    'gemini-pro',
]

print("🧪 Testing available models...\n")
working_model = None

for model_name in models_to_test:
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name, 
            google_api_key=api_key, 
            temperature=0.1
        )
        # Try to invoke
        response = llm.invoke("Say 'OK'")
        print(f"✅ {model_name}: WORKING")
        if not working_model:
            working_model = model_name
    except Exception as e:
        error_msg = str(e)[:120]
        print(f"❌ {model_name}: {error_msg}")

print(f"\n{'='*60}")
if working_model:
    print(f"✅ RECOMMENDED MODEL: {working_model}")
else:
    print(f"⚠️  None of the models worked. Check API key validity.")
