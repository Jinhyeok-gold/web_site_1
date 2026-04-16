import os
import socket
import ssl
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv(override=True)

def final_socket_test():
    api_key = os.getenv('YOUTH_CENTER_KEY', '').strip()
    host, ip, port = "www.youthcenter.go.kr", "210.90.169.167", 443
    path = f"/opi/youthPlcyList.do?display=10&pageIndex=1&openApiVlak={api_key}"
    
    print(f"🚀 Robust Socket Test to {host} ({ip})...")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((ip, port), timeout=12) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                req = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n"
                ssock.sendall(req.encode())
                
                raw_data = b""
                while True:
                    chunk = ssock.recv(8192)
                    if not chunk: break
                    raw_data += chunk
        
        header_end = raw_data.find(b"\r\n\r\n")
        headers = raw_data[:header_end].decode('utf-8', errors='ignore')
        body_raw = raw_data[header_end+4:]
        
        print(f"Headers received (Length: {len(headers)})")
        
        if "Transfer-Encoding: chunked" in headers:
            print("Detected Chunked Encoding, merging...")
            final_body = b""
            pos = 0
            while pos < len(body_raw):
                c_end = body_raw.find(b"\r\n", pos)
                if c_end == -1: break
                c_len = int(body_raw[pos:c_end].split(b";")[0], 16)
                if c_len == 0: break
                final_body += body_raw[c_end+2 : c_end+2+c_len]
                pos = c_end + 2 + c_len + 2
            body = final_body.decode('utf-8', errors='ignore')
        else:
            body = body_raw.decode('utf-8', errors='ignore')

        if "<youthPolicy>" in body:
            print("✅ SUCCESS: Found <youthPolicy> in decoded body!")
            root = ET.fromstring(body)
            policies = root.findall('.//youthPolicy')
            print(f"Items found: {len(policies)}")
        else:
            print(f"❌ FAIL: Policy tag not found. Body snippet: {body[:200]}")

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    final_socket_test()
