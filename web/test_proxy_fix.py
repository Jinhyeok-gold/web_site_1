import os
import requests
from urllib.parse import unquote
from dotenv import load_dotenv

load_dotenv(override=True)

def test_no_proxy():
    youth_key = os.getenv('YOUTH_CENTER_KEY', '').strip()
    url = "https://www.youthcenter.go.kr/opi/youthPlcyList.do"
    params = {'openApiVlak': youth_key, 'display': 1, 'pageIndex': 1}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    print("--- [Test with trust_env=False] ---")
    session = requests.Session()
    session.trust_env = False  # Disable picking up system/env proxies
    
    try:
        # Try HTTPS
        print("Trying HTTPS with trust_env=False...", end=" ", flush=True)
        res = session.get(url, params=params, headers=headers, timeout=10)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print("✅ SUCCESS")
        else:
            print(f"❌ FAIL (Response: {res.text[:50]}...)")
    except Exception as e:
        print(f"❌ ERROR: {e}")

    print("\n--- [Test with urllib as alternative] ---")
    import urllib.request
    try:
        print("Trying urllib.request.urlopen...", end=" ", flush=True)
        full_url = f"{url}?openApiVlak={youth_key}&display=1&pageIndex=1"
        req = urllib.request.Request(full_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"Status: {response.getcode()}")
            print("✅ SUCCESS")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_no_proxy()
