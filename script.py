import os
import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import socket

# --- CONFIGURATION: PLEASE EDIT THESE VALUES ---
FORUM_PAGE_URL = "" # e.g. https://fuoverflow.com/threads/cea201-fa-2024-re.3059/
USER_COOKIE = "" <- add ur cucki here
BASE_URL = "https://fuoverflow.com"
MAX_CONCURRENT_DOWNLOADS = 50
# --- END OF CONFIGURATION ---

def parse_cookie(cookie_str):
    """Parses cookie string into a dictionary"""
    cookies = {}
    for item in cookie_str.split(';'):
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key.strip()] = value.strip()
    return cookies

def get_download_dir(url):
    """Derives a directory name from the given URL."""
    try:
        path = urlparse(url).path
        return [part for part in path.split('/') if part][-1]
    except IndexError:
        print("⚠️ Using 'attachments' as download directory")
        return "attachments"

async def download_file(session, semaphore, url, filepath):
    """Asynchronously downloads and saves a file with semaphore control"""
    async with semaphore:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                async with aiofiles.open(filepath, 'wb') as f:
                    await f.write(await response.read())
            return None
        except Exception as e:
            return f"Failed to download {os.path.basename(filepath)}: {str(e)}"

async def fetch_page(session, url):
    """Fetches HTML content of a page"""
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"❌ Failed to fetch page: {str(e)}")
        return None

async def main():
    # Warm DNS cache (optional but helpful)
    try:
        socket.getaddrinfo('fuoverflow.com', 443)
    except socket.gaierror:
        pass

    DOWNLOAD_DIR = get_download_dir(FORUM_PAGE_URL)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    print(f"📁 Download directory: {DOWNLOAD_DIR}")

    # Create aiohttp session with persistent cookies
    cookies = parse_cookie(USER_COOKIE) if USER_COOKIE else None
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_DOWNLOADS * 2)
    
    async with aiohttp.ClientSession(
        connector=connector,
        cookies=cookies,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    ) as session:
        # Fetch forum page
        print(f"🌐 Fetching: {FORUM_PAGE_URL}")
        html = await fetch_page(session, FORUM_PAGE_URL)
        if not html:
            return

        # Parse attachments
        soup = BeautifulSoup(html, 'lxml')
        attachment_links = soup.select('a.file-preview[href^="/attachments/"]')
        
        if not attachment_links:
            print("❌ No attachments found - check URL/cookie/selectors")
            return

        print(f"🔍 Found {len(attachment_links)} attachments")
        
        # Prepare download tasks
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
        tasks = []
        download_count = 0
        
        for link in attachment_links:
            file_url = urljoin(BASE_URL, link['href'])
            
            # Get filename
            if img := link.find('img', alt=True):
                filename = img['alt']
            else:
                filename = link['href'].split('/')[-1]
            
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            
            if os.path.exists(filepath):
                continue
                
            download_count += 1
            tasks.append(download_file(session, semaphore, file_url, filepath))
        
        # Run downloads
        if not tasks:
            print("✅ All files already downloaded")
            return
            
        print(f"🚀 Downloading {download_count} files concurrently...")
        start_time = time.perf_counter()
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results
        errors = 0
        for result in results:
            if result and not isinstance(result, Exception):
                print(f"⚠️ {result}")
                errors += 1
        
        total_time = time.perf_counter() - start_time
        print(
            f"\n🏁 Downloads completed in {total_time:.2f} seconds | "
            f"{download_count - errors} succeeded | "
            f"{errors} failed"
        )
        print(f"💾 Files saved to: {os.path.abspath(DOWNLOAD_DIR)}")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    print("⚡ Starting asynchronous downloader ⚡")
    asyncio.run(main())