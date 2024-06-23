import bs4
import requests
from collections import deque


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
    return url.startswith("https://") or url.startswith("http://")


def main(base_url: str):
    domain = get_domain_name(base_url)
    print(domain)
    explored_urls = set()
    exploring_urls = set()
    queue = deque()

    # basically, we can do a bfs from the base url
    queue.append(base_url)
    while len(queue) > 0:
        url = queue.popleft()
        explored_urls.add(url)
        soup = bs4.BeautifulSoup(requests.get(url).text, "html.parser")

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
                queue.append(href)
                exploring_urls.add(href)

    return explored_urls


if __name__ == "__main__":
    main(base_url="https://rev.ai/")
