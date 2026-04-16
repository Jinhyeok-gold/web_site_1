import os
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from dotenv import load_dotenv

load_dotenv(override=True)

def verify_all():
    raw_portal_key = os.getenv('DATA_PORTAL_KEY', '').strip()
    youth_key = os.getenv('YOUTH_CENTER_KEY', '').strip()
    fss_key = os.getenv('FSS_FINANCE_KEY', '').strip()
    google_key = os.getenv('GOOGLE_API_KEY', '').strip()
    
    decoded_portal_key = unquote(raw_portal_key)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    results = []

    print("🔍 [API Comprehensive Audit v20]")
    print("-" * 50)

    # 1. Public Data Portal (Welfare/Bokjiro)
    print("1. DATA_PORTAL_KEY (Bokjiro) ...", end=" ", flush=True)
    try:
        url = "http://apis.data.go.kr/B554287/NationalWelfareInformationsV001/NationalWelfarelistV001"
        params = {'serviceKey': decoded_portal_key, 'callTp': 'L', 'srchKeyCode': '001', 'numOfRows': 1, 'pageNo': 1}
        res = requests.get(url, params=params, headers=headers, timeout=10, proxies={'http': None, 'https': None})
        if res.status_code == 200 and "<servList>" in res.text:
            print("✅ OK")
            results.append(("DATA_PORTAL_KEY", "OK"))
        else:
            print("❌ FAIL (Check if encoded key is needed)")
            results.append(("DATA_PORTAL_KEY", "FAIL"))
    except:
        print("❌ ERROR (Timeout/Connection)")
        results.append(("DATA_PORTAL_KEY", "ERROR"))

    # 2. Youth Center API
    print("2. YOUTH_CENTER_KEY (Youth Policy) ...", end=" ", flush=True)
    try:
        # HTTPS then HTTP fallback
        url_https = "https://www.youthcenter.go.kr/opi/youthPlcyList.do"
        url_http = "http://www.youthcenter.go.kr/opi/youthPlcyList.do"
        params = {'openApiVlak': youth_key, 'display': 1, 'pageIndex': 1}
        try:
            res = requests.get(url_https, params=params, headers=headers, timeout=10, proxies={'http': None, 'https': None})
        except:
            res = requests.get(url_http, params=params, headers=headers, timeout=10, proxies={'http': None, 'https': None})
            
        if res.status_code == 200 and ("<youthPolicy>" in res.text or "<resultCode>00</resultCode>" in res.text):
            print("✅ OK")
            results.append(("YOUTH_CENTER_KEY", "OK"))
        else:
            print("❌ FAIL (Check secret key validity)")
            results.append(("YOUTH_CENTER_KEY", "FAIL"))
    except:
        print("❌ ERROR (Timeout/Connection)")
        results.append(("YOUTH_CENTER_KEY", "ERROR"))

    # 3. FSS Finance API
    print("3. FSS_FINANCE_KEY (Bank Products) ...", end=" ", flush=True)
    try:
        url = "http://finlife.fss.or.kr/finlifeapi/rentHouseLoanProductsSearch.json"
        params = {'auth': fss_key, 'topFinGrpNo': '020000', 'pageNo': 1}
        res = requests.get(url, params=params, headers=headers, timeout=10, proxies={'http': None, 'https': None})
        if res.status_code == 200 and res.json().get('result', {}).get('err_cd') == '000':
            print("✅ OK")
            results.append(("FSS_FINANCE_KEY", "OK"))
        else:
            print("❌ FAIL")
            results.append(("FSS_FINANCE_KEY", "FAIL"))
    except:
        print("❌ ERROR")
        results.append(("FSS_FINANCE_KEY", "ERROR"))

    # 4. Google Gemini API
    print("4. GOOGLE_API_KEY (AI Chatbot) ...", end=" ", flush=True)
    try:
        # Using a more standard endpoint for verification
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={google_key}"
        payload = {"contents": [{"parts": [{"text": "hi"}]}]}
        res = requests.post(url, json=payload, timeout=10, proxies={'http': None, 'https': None})
        
        if res.status_code == 200:
            print("✅ OK")
            results.append(("GOOGLE_API_KEY", "OK"))
        elif res.status_code == 404:
            # Try 1.5-flash-latest if 1.5-flash fails
            url_alt = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={google_key}"
            res_alt = requests.post(url_alt, json=payload, timeout=10, proxies={'http': None, 'https': None})
            if res_alt.status_code == 200:
                print("✅ OK (latest)")
                results.append(("GOOGLE_API_KEY", "OK"))
            else:
                print(f"❌ FAIL (Status {res_alt.status_code})")
                results.append(("GOOGLE_API_KEY", "FAIL"))
        else:
            print(f"❌ FAIL (Status {res.status_code}: {res.text[:100]}...)")
            results.append(("GOOGLE_API_KEY", "FAIL"))
    except Exception as e:
        print(f"❌ ERROR ({e})")
        results.append(("GOOGLE_API_KEY", "ERROR"))

    print("-" * 50)
    print("Audit Complete.")

if __name__ == "__main__":
    verify_all()
