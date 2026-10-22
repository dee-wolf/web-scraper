from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict

class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

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
