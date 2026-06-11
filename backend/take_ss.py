import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:3000/')
        await page.click('.feedback-btn')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='C:/Users/kiend/.gemini/antigravity/brain/2397a54f-f17f-4ecf-9c38-571206323cf7/artifacts/feedback_modal_preview.png')
        await browser.close()

asyncio.run(main())
