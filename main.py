import sys
from crawl import crawl_site_async
import asyncio

async def main():
    if len(sys.argv) != 4:
        print("usage: main.py URL max_concurrency max_page")
        sys.exit(1)
    base_url = sys.argv[1]
    max_concurrency = int(sys.argv[2])
    max_pages = int(sys.argv[3])
    page_data = await crawl_site_async(base_url, max_concurrency, max_pages)
    print(f"You've found {len(page_data)} pages.")
    for page in page_data.values():
        print(f'On {page["url"]}, there were {len(page["outgoing_links"])} links.')

if __name__ == "__main__":
    asyncio.run(main())
