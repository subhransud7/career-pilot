from playwright.async_api import async_playwright


class FetchService:

    async def fetch(self, url: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(storage_state="linkedin_session.json")
            page = await context.new_page()

            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            # Wait for LinkedIn post container
            await page.wait_for_selector(
                "div.feed-shared-update-v2",
                timeout=15000
            )

            content = await page.content()

            await browser.close()

            return content
