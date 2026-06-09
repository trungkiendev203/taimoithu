import sys
from app.services.helpers import get_cookies_file_path, convert_json_to_netscape

print("Finding cookies...")
path = get_cookies_file_path()
print(f"Result path: {path}")

# manually try conversion
import json
json_path = "backend/cookies.txt"
with open(json_path, 'r', encoding='utf-8') as f:
    cookies = json.load(f)
    print(f"Loaded {len(cookies)} cookies from {json_path}")
    
res = convert_json_to_netscape(json_path, "backend/cookies_converted.txt")
print(f"Conversion result: {res}")
