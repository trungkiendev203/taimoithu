import asyncio
import httpx

async def test():
    try:
        url = 'https://p16-common-sign.tiktokcdn-us.com/tos-alisg-i-photomode-sg/7fba61ef6d1647e48b7a930117559bb1~tplv-photomode-image.jpeg?dr=9616&x-expires=1780484400&x-signature=EpkzSaLTWDplZvoya2tLT9D1FVY%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=9b759fb9&idc=useast8&ftpl=1'
        client = httpx.AsyncClient()
        resp = await client.get(url, headers={'Referer': 'https://www.instagram.com/'})
        print("Status code:", resp.status_code)
    except Exception as e:
        print("Error:", e)

asyncio.run(test())
