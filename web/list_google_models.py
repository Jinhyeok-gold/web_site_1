import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

def list_gemini_models():
    api_key = os.getenv('GOOGLE_API_KEY', '').strip()
    if not api_key:
        print("❌ No GOOGLE_API_KEY found.")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            models = res.json().get('models', [])
            print("✅ Available Models:")
            for m in models:
                print(f"  - {m['name']} (Supports: {m['supportedGenerationMethods']})")
        else:
            print(f"❌ Failed to list models: {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_gemini_models()
