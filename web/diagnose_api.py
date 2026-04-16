import os
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from dotenv import load_dotenv

load_dotenv()

def test_api():
    raw_key = os.getenv('DATA_PORTAL_KEY')
    youth_key = os.getenv('YOUTH_CENTER_KEY')
    fss_key = os.getenv('FSS_FINANCE_KEY')
    decoded_key = unquote(raw_key) if raw_key else ""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    print("=== API Connectivity Test ===")

    # 1. Welfare (Bokjiro) - uses DATA_PORTAL_KEY (decoded)
    print("\n[1] Testing Welfare (Bokjiro)...")
    url_welfare = "http://apis.data.go.kr/B554287/NationalWelfareInformationsV001/NationalWelfarelistV001"
    params = {'serviceKey': decoded_key, 'callTp': 'L', 'srchKeyCode': '001', 'numOfRows': 1, 'pageNo': 1}
    try:
        res = requests.get(url_welfare, params=params, headers=headers, timeout=10, proxies={'http': None, 'https': None})
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            if "<returnAuthMsg>SERVICE_KEY_IS_NOT_REGISTERED_ERROR</returnAuthMsg>" in res.text:
                 print("Result: FAIL (Key not registered)")
            elif "<returnAuthMsg>LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR</returnAuthMsg>" in res.text:
                 print("Result: FAIL (Quota exceeded)")
            elif "<servList>" in res.text:
                 print("Result: SUCCESS")
            else:
                 print(f"Result: UNKNOWN (Response snippet: {res.text[:100]}...)")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Youth Center - uses YOUTH_CENTER_KEY
    print("\n[2] Testing Youth Center...")
    url_youth = "http://www.youthcenter.go.kr/opi/youthPlcyList.do"
    params = {'openApiVlak': youth_key, 'display': 1, 'pageIndex': 1}
    try:
        res = requests.get(url_youth, params=params, headers=headers, timeout=10, proxies={'http': None, 'https': None})
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            if "<resultCode>00</resultCode>" in res.text or "<youthPolicy>" in res.text:
                print("Result: SUCCESS")
            else:
                print(f"Result: FAIL (Response snippet: {res.text[:100]}...)")
    except Exception as e:
        print(f"Error: {e}")

    # 3. FSS Finance - uses FSS_FINANCE_KEY
    print("\n[3] Testing FSS Finance...")
    url_fss = "http://finlife.fss.or.kr/finlifeapi/rentHouseLoanProductsSearch.json"
    params = {'auth': fss_key, 'topFinGrpNo': '020000', 'pageNo': 1}
    try:
        res = requests.get(url_fss, params=params, headers=headers, timeout=10)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            if data.get('result', {}).get('err_cd') == '000':
                print("Result: SUCCESS")
            else:
                print(f"Result: FAIL ({data.get('result', {}).get('err_msg')})")
    except Exception as e:
        print(f"Error: {e}")

    # 4. ApplyHome (ODCloud) - uses DATA_PORTAL_KEY (raw)
    print("\n[4] Testing ApplyHome (ODCloud)...")
    url_apply = "https://api.odcloud.kr/api/ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail"
    params = {'page': 1, 'perPage': 1, 'serviceKey': raw_key}
    try:
        res = requests.get(url_apply, params=params, headers=headers, timeout=10)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print("Result: SUCCESS")
        elif res.status_code == 401:
            print("Result: FAIL (Unauthorized - Key might be wrong)")
        else:
            print(f"Result: FAIL (Status {res.status_code})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
