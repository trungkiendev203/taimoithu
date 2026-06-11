import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        # Test valid payload
        res = await client.post('http://localhost:8000/api/v1/feedback', json={
            "message": "This is a valid message"
        })
        print("Valid payload:", res.status_code, res.text)
        
        # Test invalid payload (message too short)
        res = await client.post('http://localhost:8000/api/v1/feedback', json={
            "message": "abc"
        })
        print("Invalid payload:", res.status_code, res.text)

asyncio.run(test())
