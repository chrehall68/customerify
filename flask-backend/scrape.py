import bs4
import aiohttp
from asyncio.queues import Queue
import asyncio
from typing import Callable, Awaitable
import uuid


def get_domain_name(url: str) -> str:
    # find the domain name and remove potential subdomains
    last_dot = url.rindex(".")
    domain_start = url.index("//") + 2
    if "." in url[domain_start:last_dot]:
        domain_start = url[domain_start:last_dot].rindex(".") + 1

    domain_end = len(url)
    if "/" in url[last_dot:]:
        domain_end = url.index("/", last_dot)
    return url[domain_start:domain_end]


def is_same_domain(url: str, domain: str) -> bool:
    # strip leading slashes
    url = url.removeprefix("https://").removeprefix("http://")
    # now just check if the substring `domain` appears in url
    if domain not in url:
        return False
    # make sure that it appears before any slashes
    return "/" not in url or url.index(domain) < url.index("/")


def is_valid_url(url: str) -> bool:
    denied_prefixes = [".xml", ".json", ".pdf", ".mp3", ".wav", ".webp", ".webm"]
    return (url.startswith("https://") or url.startswith("http://")) and not any(
        url.endswith(prefix) for prefix in denied_prefixes
    )


async def main(
    base_url: str,
    max_urls: int = -1,
    timeout: int = 5,
    document_callback: Callable[[bs4.BeautifulSoup, str], Awaitable[None]] = None,
) -> set:
    if max_urls == -1:
        max_urls = float("inf")
    domain = get_domain_name(base_url)
    print(domain)
    explored_urls = set()
    exploring_urls = set()
    queue = Queue()

    async with aiohttp.ClientSession() as session:
        # basically, we can do a bfs from the base url
        await queue.put(base_url)

        async def helper(url: str):
            explored_urls.add(url)
            soup = bs4.BeautifulSoup(
                await (await session.get(url, timeout=timeout)).text(), "html.parser"
            )
            for link in soup.find_all("a"):
                href = link.get("href", "")
                if not is_valid_url(href) and href.startswith("/"):
                    href = base_url + href
                if (
                    is_valid_url(href)
                    and href not in explored_urls
                    and href not in exploring_urls
                    and is_same_domain(href, domain)
                ):
                    await queue.put(href)
                    exploring_urls.add(href)

            if document_callback:
                await document_callback(soup, str(uuid.uuid4()))

        while queue.qsize() > 0 and len(explored_urls) < max_urls:
            # take all the urls from the queue
            urls = []
            for _ in range(queue.qsize()):
                urls.append(await queue.get())
            # filter urls
            urls = list(filter(lambda url: url not in explored_urls, urls))
            urls = list(set(urls))  # take only unique urls
            await asyncio.gather(*[helper(url) for url in urls])

    return explored_urls


if __name__ == "__main__":
    import datetime

    start = datetime.datetime.now()
    results = asyncio.run(main(base_url="https://rev.ai/"))
    end = datetime.datetime.now()
    print((end - start).total_seconds())
    print(results)
