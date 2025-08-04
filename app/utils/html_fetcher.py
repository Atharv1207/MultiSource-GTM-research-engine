import asyncio
import aiohttp
import logging
import hashlib
import requests
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import time
from pathlib import Path
from typing import List, Optional

# Setup cache
CACHE_DIR = Path(".cache/html")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )
}
CACHE_EXPIRY_SECONDS = 60 * 60 * 24  # 24 hours

# Concurrency limiter
semaphore = asyncio.Semaphore(10)


def fetch_html(url: str, timeout: int = 10) -> Optional[str]:
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.warning(f"[HTML FETCH] Failed to fetch {url}: {e}")
        return None


def extract_main_content(html: str, url: Optional[str] = None) -> str:
    downloaded = trafilatura.extract(html, include_comments=False, include_tables=True)
    if downloaded:
        return downloaded.strip()

    try:
        doc = Document(html)
        summary_html = doc.summary()
        soup = BeautifulSoup(summary_html, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        return text.strip()
    except Exception as e:
        logging.warning(f"[CONTENT EXTRACT] Error parsing fallback content: {e}")
        return ""


def fetch_and_extract(url: str) -> Optional[str]:
    html = fetch_html(url)
    if not html:
        return None
    return extract_main_content(html)


def get_cache_path(url: str) -> Path:
    hash_val = hashlib.md5(url.encode()).hexdigest()
    return CACHE_DIR / f"{hash_val}.html"


def is_cache_valid(path: Path) -> bool:
    return path.exists() and (time.time() - path.stat().st_mtime) < CACHE_EXPIRY_SECONDS


def load_from_cache(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def save_to_cache(path: Path, content: str):
    try:
        path.write_text(content, encoding="utf-8")
    except Exception:
        pass


async def fetch(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    cache_path = get_cache_path(url)
    if is_cache_valid(cache_path):
        logging.info(f"[CACHE] Loaded from cache: {url}")
        return load_from_cache(cache_path)

    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                html = await response.text()
                save_to_cache(cache_path, html)
                return html
            else:
                logging.warning(f"[FETCH] Non-200 status for {url}: {response.status}")
                return None
    except Exception as e:
        logging.warning(f"[FETCH] Error fetching {url}: {e}")
        return None


async def fetch_with_limit(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    async with semaphore:
        return await fetch(session, url)


async def fetch_all(urls: List[str]) -> List[Optional[str]]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_with_limit(session, url) for url in urls]
        return await asyncio.gather(*tasks)


async def fetch_and_extract_all(urls: List[str]) -> List[str]:
    htmls = await fetch_all(urls)
    return [extract_main_content(html) if html else "" for html in htmls]
