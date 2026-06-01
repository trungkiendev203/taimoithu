import requests
import base64

def verify():
    url = 'https://p16-common-sign.tiktokcdn-us.com/tos-alisg-i-photomode-sg/7fba61ef6d1647e48b7a930117559bb1~tplv-photomode-image.jpeg?dr=9616&x-expires=1780484400&x-signature=EpkzSaLTWDplZvoya2tLT9D1FVY%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=9b759fb9&idc=useast8&ftpl=1'
    b64_url = base64.urlsafe_b64encode(url.encode()).decode().rstrip('=')
    
    # Simulate frontend replacing + with space if not url encoded
    test_url = b64_url.replace("+", " ")
    
    res = requests.get(f'http://localhost:8000/api/v1/proxy-image?url=base64:{test_url}')
    print("Status code:", res.status_code)
    if res.status_code != 200:
        print("Error content:", res.text)
        
verify()
