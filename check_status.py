import httpx
import json

try:
    r = httpx.get("http://localhost:8005/apk/status")
    print(f"Status: {r.status_code}")
    print(r.json())
    
    r2 = httpx.get("http://localhost:8005/apk/list")
    print(f"List: {r2.status_code}")
    print(json.dumps(r2.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
