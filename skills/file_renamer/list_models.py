import google.generativeai as genai

API_KEY = "AIzaSyCW7aJCBWLKQkGfBnC8nhC2jC1UWFXPilY"
genai.configure(api_key=API_KEY)

print("Listing models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Name: {m.name}")
except Exception as e:
    print(f"Error: {e}")
