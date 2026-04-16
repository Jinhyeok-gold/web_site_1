import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

def exhaustive_probe():
    key = os.getenv('GOOGLE_API_KEY', '').strip()
    print(f"🔬 Exhaustive Probe for Key: {key[:10]}...")
    
    models = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-pro', 'gemini-pro', 'gemini-1.0-pro']
    versions = ['v1', 'v1beta']
    
    found = False
    for v in versions:
        for m in models:
            print(f"Testing {v}/{m}...", end=" ", flush=True)
            url = f"https://generativelanguage.googleapis.com/{v}/models/{m}:generateContent?key={key}"
            payload = {"contents": [{"parts": [{"text": "hi"}]}]}
            try:
                res = requests.post(url, json=payload, timeout=5)
                if res.status_code == 200:
                    print("✅ SUCCESS!")
                    found = True
                    break
                else:
                    print(f"❌ {res.status_code}")
            except Exception as e:
                print(f"❌ Error: {e}")
        if found: break
    
    if not found:
        print("\nSearching for ANY available models for this key...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        res = requests.get(url)
        print(f"ListModels Status: {res.status_code}")
        print(f"Response: {res.text[:500]}")

if __name__ == "__main__":
    exhaustive_probe()
