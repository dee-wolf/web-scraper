from urllib.parse import urlsplit
from bs4 import BeautifulSoup, Tag

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
