from typing import Optional

import aiohttp

__all__ = [
    "WebTool"
]


class WebTool:

    def __init__(self, url: Optional[str]):
        self.url = url

    async def get_html_content(self) -> Optional[str]:
        async with aiohttp.ClientSession() as session:
            async with session.request("GET", self.url) as request:
                return await request.text()
