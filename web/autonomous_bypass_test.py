import socket
import ssl
import re
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

load_dotenv(override=True)

def autonomous_socket_bypass():
    api_key = os.getenv('YOUTH_CENTER_KEY', '').strip()
    host = "www.youthcenter.go.kr"
    ip = "210.90.169.167"
    port = 443
    
    # Starting path
    current_path = f"/opi/youthPlcyList.do?display=5&pageIndex=1&openApiVlak={api_key}"
    
    print(f"🚀 Starting Autonomous Bypass Loop for {host}...")
    
    def fetch_raw(target_path):
        print(f"  -> Fetching: {target_path[:60]}...")
        context = ssl.create_default_context()
        try:
            with socket.create_connection((ip, port), timeout=15) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    request = (
                        f"GET {target_path} HTTP/1.1\r\n"
                        f"Host: {host}\r\n"
                        f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n"
                        f"Connection: close\r\n\r\n"
                    )
                    ssock.sendall(request.encode())
                    
                    data = b""
                    while True:
                        chunk = ssock.recv(16384)
                        if not chunk: break
                        data += chunk
                    return data
        except Exception as e:
            print(f"  ❌ Socket Error: {e}")
            return None

    for attempt in range(3): # Max 3 redirects
        raw_res = fetch_raw(current_path)
        if not raw_res: break
        
        header_end = raw_res.find(b"\r\n\r\n")
        headers = raw_res[:header_end].decode('utf-8', errors='ignore')
        body_raw = raw_res[header_end+4:]
        
        # Check Status
        status_line = headers.split("\r\n")[0]
        print(f"  Status: {status_line}")
        
        if "302" in status_line or "301" in status_line:
            loc = re.search(r"Location: (.*)\r\n", headers, re.IGNORECASE)
            if loc:
                current_path = loc.group(1).strip()
                if current_path.startswith("http"): # Full URL case
                    # Strip to path
                    current_path = "/" + current_path.split("/", 3)[-1]
                continue
        
        # Success or other
        if "200 OK" in status_line:
            # Handle Chunked
            if "Transfer-Encoding: chunked" in headers:
                print("  Decoding Chunks...")
                final_body = b""
                pos = 0
                while pos < len(body_raw):
                    l_end = body_raw.find(b"\r\n", pos)
                    if l_end == -1: break
                    chunk_len = int(body_raw[pos:l_end].split(b";")[0], 16)
                    if chunk_len == 0: break
                    final_body += body_raw[l_end+2 : l_end+2+chunk_len]
                    pos = l_end + 2 + chunk_len + 2
                body = final_body.decode('utf-8', errors='ignore')
            else:
                body = body_raw.decode('utf-8', errors='ignore')
            
            if "<youthPolicy>" in body:
                print("  ✅ SUCCESS: Data retrieved autonomously!")
                return True
            else:
                print(f"  ❌ FAIL: No policy tags. Body snippet: {body[:200]}")
                return False
        break
    return False

if __name__ == "__main__":
    autonomous_socket_bypass()
