import os
import json
import subprocess
from app.core.apk_config import settings
from app.utils.apk_consts import (
    ensure_dirs, create_lock_payload, write_lock,
    clear_lock, read_apk_list, write_apk_list
)
from app.utils.repo_manager import clone_or_update_repo
from app.utils.bundle_utils import fetch_manifest, extract_all_asset_filenames, get_sas_url
from app.utils.apk_downloader import download_assets
from app.utils.apk_builder import build_apk
import shutil

def check_environment():
    """Verify that required tools are installed and accessible."""
    tools = {
        "npm": ["npm", "--version"],
        "node": ["node", "--version"],
        "git": ["git", "--version"],
        "java": ["java", "-version"]
    }
    for name, cmd in tools.items():
        try:
            # On Windows, npm/java might not return 0 for just checking version depending on setup, 
            # but we just want to see if the command exists.
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            print(f"⚠️ Warning: '{name}' command not found or failed. Build might fail.")

async def generate_apk(lang_id: str, draft: bool=False):
    ensure_dirs()
    check_environment()
    if os.path.exists(settings.LOCK_FILE):
        raise RuntimeError("Another generation is already in progress")

    write_lock(create_lock_payload(lang_id, draft))

    try:
        print(f"🌍 Starting APK generation for {lang_id} (draft={draft})")

        clone_or_update_repo()

        manifest = await fetch_manifest(lang_id, settings.LME_BASE_URL, settings.LME_AUTH_TOKEN)
        print(f"✅ Fetched manifest for {lang_id}")

        sas_url = await get_sas_url(settings.LME_BASE_URL, settings.LME_AUTH_TOKEN)
        print("✅ Fetched SAS URL")

        assets = extract_all_asset_filenames(manifest)
        print(f"📦 Found {len(assets)} assets for {lang_id}")

        manifest_dir = os.path.abspath(settings.MANIFEST_OUTPUT_DIR)
        assets_dir = os.path.abspath(settings.ASSETS_OUTPUT_DIR)
        
        # 🧹 Clear old files to ensure a "perfect" clean state
        for d in [manifest_dir, assets_dir]:
            if os.path.exists(d):
                print(f"🧹 Cleaning directory: {d}")
                shutil.rmtree(d)
            os.makedirs(d, exist_ok=True)

        manifest_path = os.path.join(manifest_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"✅ Wrote manifest to {manifest_path}")

        await download_assets(assets, sas_url, assets_dir)
        print(f"✅ Downloaded all assets to {assets_dir}")

        apk_meta = build_apk(lang_id, draft)

        apk_list = read_apk_list()
        lang_list = apk_list.get(lang_id, [])
        lang_list.append(apk_meta)
        apk_list[lang_id] = lang_list
        write_apk_list(apk_list)

        print(f"✅ APK metadata saved for {lang_id}")
        return apk_meta

    finally:
        clear_lock()
