import os
import asyncio
import httpx
from typing import List

DOWNLOAD_CHUNK = 64 * 1024
MAX_CONCURRENT_DOWNLOADS = 10

async def _download_one(client: httpx.AsyncClient, url: str, dest: str, idx: int, total: int):
    """Download a single file."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        async with client.stream("GET", url) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as f:
                async for chunk in resp.aiter_bytes(DOWNLOAD_CHUNK):
                    f.write(chunk)
        print(f"✅ [{idx + 1}/{total}] Downloaded: {os.path.basename(dest)}")
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        raise

async def download_assets(asset_ids: List[str], sas_url: str, dest_folder: str):
    """Download all assets to dest_folder with concurrency limit and full waiting."""
    base, query = sas_url.split("?", 1)
    total = len(asset_ids)
    if total == 0:
        print("⚠️ No assets to download.")
        return

    print(f"🚀 Starting download of {total} assets...")

    sem = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)

    async with httpx.AsyncClient(timeout=180.0) as client:
        async def sem_download(idx, asset):
            async with sem:
                url = f"{base}/{asset}?{query}"
                dest = os.path.join(dest_folder, asset)
                await _download_one(client, url, dest, idx, total)

        # ✅ Ensure FastAPI waits for all downloads
        await asyncio.gather(*(sem_download(idx, a) for idx, a in enumerate(asset_ids)))

    print(f"✅ All {total} assets downloaded successfully.")
