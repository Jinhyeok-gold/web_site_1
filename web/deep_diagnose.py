import os
import socket
import requests
import json
from dotenv import load_dotenv

load_dotenv(override=True)

def deep_diagnose():
    google_key = os.getenv('GOOGLE_API_KEY', '').strip()
    youth_key = os.getenv('YOUTH_CENTER_KEY', '').strip()
    
    print("🔬 [Deep Environment Diagnosis]")
    print("-" * 50)

    # 1. Socket Connectivity Test (Bypass all HTTP proxies)
    print("1. Socket Connection to YouthCenter.go.kr (Port 443)...", end=" ", flush=True)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(("210.90.169.167", 443)) # Use Resolved IP
        print("✅ SUCCESS (Direct IP works)")
        s.close()
    except Exception as e:
        print(f"❌ FAIL ({e})")

    print("2. Socket Connection to YouthCenter.go.kr (Domain Port 443)...", end=" ", flush=True)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(("www.youthcenter.go.kr", 443))
        print("✅ SUCCESS (DNS/Domain works)")
        s.close()
    except Exception as e:
        print(f"❌ FAIL ({e})")

    # 3. Google API Library Test (The real way the app connects)
    print("\n3. Testing Google GenAI Library specifically...")
    try:
        # Check which library is installed
        import google.generativeai as genai_v1
        print("Using google-generativeai library...", end=" ", flush=True)
        genai_v1.configure(api_key=google_key)
        model = genai_v1.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hi", request_options={"timeout": 10})
        print(f"✅ SUCCESS: {response.text[:20]}...")
    except Exception as e1:
        print(f"❌ google-generativeai failed: {e1}")
        try:
            from google import genai as genai_v2
            print("Trying google-genai (v2 library)...", end=" ", flush=True)
            client = genai_v2.Client(api_key=google_key)
            response = client.models.generate_content(model='gemini-1.5-flash', contents="Hi")
            print(f"✅ SUCCESS: {response.text[:20]}...")
        except Exception as e2:
            print(f"❌ google-genai failed: {e2}")

    # 4. Check for Hidden Proxy Env (Subtle names)
    print("\n4. Checking subtle Environment Variables...")
    subtle_vars = ['npm_config_proxy', 'npm_config_https_proxy', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE']
    found = False
    for v in subtle_vars:
        val = os.getenv(v)
        if val:
            print(f"Found {v}: {val}")
            found = True
    if not found: print("No hidden proxy/cert variables found.")

if __name__ == "__main__":
    deep_diagnose()
