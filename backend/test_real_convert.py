import json
from app.services.helpers import convert_json_to_netscape

json_path = "E:\\taimoithu\\cookies.txt"
out_path = "E:\\taimoithu\\backend\\test_converted_real.txt"
try:
    with open(json_path, 'r', encoding='utf-8') as f:
        cookies = json.load(f)
        print(f"Loaded {len(cookies)} cookies")
except Exception as e:
    print(f"JSON Load error: {e}")

res = convert_json_to_netscape(json_path, out_path)
print(f"Conversion result: {res}")
print(f"Conversion result: {res}")

if res:
    with open(out_path, "r", encoding="utf-8") as f:
        print(f.read(500))
