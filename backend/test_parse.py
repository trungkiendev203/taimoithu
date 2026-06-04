import urllib.parse, json, re

with open('douyin_test.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'id=" RENDER_DATA\[^>]*>([^<]+)</script>',
