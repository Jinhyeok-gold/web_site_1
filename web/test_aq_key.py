import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

def test_aq_key():
    key = os.getenv('GOOGLE_API_KEY', '').strip()
    print(f"Testing Key: {key[:10]}...")
    
    # 1. Standard Gemini API (v1beta)
    print("1. Standard Gemini v1beta...", end=" ", flush=True)
    url1 = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    payload = {"contents": [{"parts": [{"text": "hi"}]}]}
    res1 = requests.post(url1, json=payload, timeout=10)
    print(f"Status: {res1.status_code}")
    if res1.status_code != 200:
        print(f"   Error: {res1.text[:100]}")
    else:
        print("   ✅ SUCCESS")

    # 2. Alternative Model Name (gemini-pro)
    print("2. Testing gemini-pro...", end=" ", flush=True)
    url2 = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={key}"
    res2 = requests.post(url2, json=payload, timeout=10)
    print(f"Status: {res2.status_code}")
    if res2.status_code == 200:
        print("   ✅ SUCCESS")

if __name__ == "__main__":
    test_aq_key()
