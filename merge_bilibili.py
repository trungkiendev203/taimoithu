import json
import os

netscape_input = """# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.bilibili.com	TRUE	/	FALSE	1812369904	buvid3	C737816F-40FF-A5F1-0F0A-699BD1E6677104165infoc
.bilibili.com	TRUE	/	FALSE	1812369904	b_nut	1780833904
.bilibili.com	TRUE	/	FALSE	1812369905	_uuid	D61010656E-B8A4-10E2D-672F-4451D7B491A605122infoc
.bilibili.com	TRUE	/	FALSE	1815393906	buvid_fp	3af2601583a47aa841a0d911d356471d
.bilibili.com	TRUE	/	FALSE	1812468315	home_feed_column	5
.bilibili.com	TRUE	/	FALSE	1812468315	browser_resolution	1536-695
.bilibili.com	TRUE	/	FALSE	1783425908	buvid4	08D780FD-84FF-263D-E92E-EBC5C4AB576G07933-026060720-QJgxwPb5lEzKjCLBRjKY3g%3D%3D
.bilibili.com	TRUE	/	FALSE	1812369909	CURRENT_QUALITY	0
.bilibili.com	TRUE	/	FALSE	1815393912	rpdid	|(m)lkmRuR|0J'u~)|)JJmuu
.bilibili.com	TRUE	/	TRUE	1796751493	DedeUserID	3707005652961467
.bilibili.com	TRUE	/	TRUE	1796751493	DedeUserID__ckMd5	e06d1b69d091f442
.bilibili.com	TRUE	/	FALSE	1812735491	theme-tip-show	SHOWED
.bilibili.com	TRUE	/	FALSE	1812468317	theme-avatar-tip-show	SHOWED
.bilibili.com	TRUE	/	FALSE	1812735488	CURRENT_FNVAL	4048
www.bilibili.com	FALSE	/	FALSE	0	bmg_af_switch	1
www.bilibili.com	FALSE	/	FALSE	0	bmg_src_def_domain	i1.hdslb.com
www.bilibili.com	FALSE	/	FALSE	0	bmg_af_sc	{"none":{"on":1,"def":"i1.hdslb.com"},"sgp":{"on":1,"def":"i1-sgp.hdslb.com"}}
.bilibili.com	TRUE	/	FALSE	1781458689	bili_ticket	eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3ODE0NTg2ODgsImlhdCI6MTc4MTE5OTQyOCwicGx0IjotMX0.rTd7DEu75J4EHgEqNfaAW7rMSbDe2Z890X5ePFuohNg
.bilibili.com	TRUE	/	FALSE	1781458689	bili_ticket_expires	1781458628
.bilibili.com	TRUE	/	TRUE	1796751493	SESSDATA	4638d716%2C1796751491%2Cfcdd8%2A62CjBFFvHIY3Bp1hKCqr-NxDMZBb3-hlkSF-uff0ZXYypufTi_n-zQelDSYAp9Ja5s5zcSVmlvUlhQc1pzVENQN1BoWHlrV2tkWXk4czJVVzczVkhEcU1vSUI1VnJKdi1iZHEtMzZFS3AtUVI4TEJEeTJSMTFieUFVUF9NOGcyUGJ5ZmdIUjUyWUhRIIEC
.bilibili.com	TRUE	/	TRUE	1796751493	bili_jct	6d770084a188265aab3af0931c96bb90
.bilibili.com	TRUE	/	TRUE	1796751493	sid	ec6n0ubm
.bilibili.com	TRUE	/	FALSE	0	b_lsid	CC4141B5_19EB7C43D43"""

# 1. Update the backend Netscape file
backend_netscape_file = r'e:\taimoithu\backend\backend\cookies.txt'
try:
    with open(backend_netscape_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
except FileNotFoundError:
    lines = ["# Netscape HTTP Cookie File\n\n"]

# Filter out old .bilibili.com cookies
filtered_lines = [line for line in lines if not line.startswith('.bilibili.com\t') and not line.startswith('www.bilibili.com\t')]

# Append new ones
new_lines = [line + '\n' for line in netscape_input.split('\n') if not line.startswith('#') and line.strip() != '']
filtered_lines.extend(new_lines)

with open(backend_netscape_file, 'w', encoding='utf-8') as f:
    f.writelines(filtered_lines)

# 2. Update the frontend/JSON cookies.txt file
json_file = r'e:\taimoithu\cookies.txt'

try:
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        # if the user literally pasted netscape into e:\taimoithu\cookies.txt, the content might be netscape now.
        if content.startswith('# Netscape'):
            old_cookies = []
        else:
            old_cookies = json.loads(content)
except:
    old_cookies = []

# If it's a JSON array, remove old bilibili.com and append new ones as JSON
if isinstance(old_cookies, list):
    filtered_json = [c for c in old_cookies if c.get('domain') not in ['.bilibili.com', 'www.bilibili.com']]
    
    for line in new_lines:
        parts = line.strip().split('\t')
        if len(parts) == 7:
            filtered_json.append({
                "domain": parts[0],
                "hostOnly": parts[1] == 'FALSE',
                "path": parts[2],
                "secure": parts[3] == 'TRUE',
                "expirationDate": float(parts[4]),
                "name": parts[5],
                "value": parts[6]
            })
            
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_json, f, indent=4)
else:
    # If the user explicitly overwrote cookies.txt with netscape format, just leave it as netscape
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(netscape_input)

print("Merged bilibili.com cookies successfully.")
