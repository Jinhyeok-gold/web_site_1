import urllib.request
import ssl
import os
from dotenv import load_dotenv

load_dotenv(override=True)

def test_urllib_bypass():
    api_key = os.getenv('YOUTH_CENTER_KEY', '').strip()
    url = f"https://www.youthcenter.go.kr/opi/youthPlcyList.do?openApiVlak={api_key}&display=1&pageIndex=1"
    
    print(f"🚀 Testing urllib ProxyHandler bypass for {url[:50]}...")
    
    # 1. Disable System Proxy explicitly
    proxy_handler = urllib.request.ProxyHandler({})
    # 2. Disable SSL Verification (sometimes proxies mess with certs)
    ssl_context = ssl._create_unverified_context()
    https_handler = urllib.request.HTTPSHandler(context=ssl_context)
    
    opener = urllib.request.build_opener(proxy_handler, https_handler)
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with opener.open(req, timeout=10) as response:
            status = response.getcode()
            body = response.read().decode('utf-8', errors='ignore')
            print(f"Status: {status}")
            if "<youthPolicy>" in body:
                print("✅ SUCCESS!")
            else:
                print(f"❌ FAIL: Body content: {body[:100]}")
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    test_urllib_bypass()
