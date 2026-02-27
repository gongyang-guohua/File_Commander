import google.generativeai as genai
import os

# Use the key from openclaw.json
GOOGLE_API_KEY = "AIzaSyCW7aJCBWLKQkGfBnC8nhC2jC1UWFXPilY"
genai.configure(api_key=GOOGLE_API_KEY)

print("Listing available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model: {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
