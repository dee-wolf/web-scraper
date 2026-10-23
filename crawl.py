from unicodedata import normalize
from urllib.parse import urlsplit, urljoin, urlparse
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
import aiohttp
import asyncio

class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

class AsyncCrawler():
    def __init__(self, base_url, max_concurrency, max_pages):
        self.base_url = base_url
        parsed_url = urlsplit(self.base_url)
        self.base_domain = parsed_url.netloc
        self.page_data = {}
        self.visited = set()
        self.max_concurrency = max_concurrency
        self.lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session = None
        self.should_stop = False
        self.all_tasks = set()
        self.max_pages = max_pages
        print(f"base_domain is: {self.base_domain}")
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    async def add_page_visit(self, normalized_url):
        async with self.lock:
            if self.should_stop:
                return False
            if normalized_url in self.visited:
                return False
            if len(self.visited) >= self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl.")
                return False
            self.visited.add(normalized_url)
            return True
    async def get_html(self, url):
        try:
            async with self.session.get(url) as response:
                if response.status >= 400:
                    raise Exception(f"Error code: {response.status}")
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    raise Exception(f"{content_type} is not text/html")
                return await response.text()
        except Exception as e:
            raise Exception(f"network error: {e}")
    async def crawl_page(self, current_url):
        if self.should_stop:
            return
        if urlparse(current_url).netloc != self.base_domain:
            return
        normalized_url = normalize_url(current_url)
        print(f"checking {current_url} against {self.base_domain}")
        if not await self.add_page_visit(normalized_url):
            return
        print(f"crawling {current_url}")
        try:
            async with self.semaphore:
                html = await self.get_html(current_url)
        except Exception as e:
            print(f"network error: {e}")
            return
        extraction = extract_page_data(html, current_url)
        async with self.lock:
            self.page_data[normalized_url] = extraction
        tasks = []
        for link in extraction["outgoing_links"]:
            task = asyncio.create_task(self.crawl_page(link))
            tasks.append(task)
            self.all_tasks.add(task)
        try:
            await asyncio.gather(*tasks)
        finally:
            for task in tasks:
                self.all_tasks.discard(task)
    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data
async def crawl_site_async(base_url, max_concurrency, max_pages):
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
        return await crawler.crawl()

def normalize_url(url):
    split_url = urlsplit(url)
    normal_url = split_url.netloc + split_url.path
    normal_url = normal_url.rstrip("/")
    return normal_url

def get_heading_from_html(html):
    parsed = BeautifulSoup(html, "html.parser")
    heading = parsed.find("h1") or parsed.find("h2")
    return heading.get_text(strip=True) if isinstance(heading, Tag) else ""

def get_first_paragraph_from_html(html):
    parsed = BeautifulSoup(html, "html.parser")
    main_section = parsed.find("main")
    if isinstance(main_section, Tag):
         para = main_section.find("p")
    else:
        para = parsed.find("p")
    return para.get_text(strip=True) if isinstance(para, Tag) else ""

def get_urls_from_html(html, base_url):
    urls = []
    parsed = BeautifulSoup(html, "html.parser")
    brackets = parsed.find_all("a")
    for bracket in brackets:
        href = bracket.get("href")
        joined = urljoin(base_url, href)
        urls.append(joined)
    return urls

def get_images_from_html(html, base_url):
    urls = []
    parsed = BeautifulSoup(html, "html.parser")
    brackets = parsed.find_all("img")
    for bracket in brackets:
        img = bracket.get("src")
        if not img:
            continue
        joined = urljoin(base_url, img)
        urls.append(joined)
    return urls

def extract_page_data(html, page_url):
    return {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }
