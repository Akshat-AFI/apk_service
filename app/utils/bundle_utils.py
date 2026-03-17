import httpx
from typing import Dict, Any, List

async def fetch_manifest(lang_id: str, base_url: str, auth_token: str) -> Dict[str, Any]:
    """Fetch the full language manifest from the LME API (v2)"""
    url = f"{base_url}/v1/clients/manifest/{lang_id}"
    headers = {"X-Internal-Sec-Access": auth_token} if auth_token else {}
    async with httpx.AsyncClient(timeout=180) as client:
        res = await client.get(url, headers=headers)
        res.raise_for_status()
        return res.json()

async def get_sas_url(base_url: str, auth_token: str) -> str:
    """Get the SAS URL for blob access"""
    url = f"{base_url}/assets/generate-sas-url"
    headers = {"X-Internal-Sec-Access": auth_token} if auth_token else {}
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        res.raise_for_status()
        return res.json()["sas_url"]

def extract_all_asset_filenames(manifest: Dict[str, Any]) -> List[str]:
    """Extract all resolvable asset filenames from the LME manifest"""
    assets = set()
    
    # 1. language_assets
    language_assets = manifest.get("language_assets", [])
    if isinstance(language_assets, list):
        for la in language_assets:
            if isinstance(la, str) and la:
                assets.add(la)
                
    # 2. category.assets
    categories = manifest.get("categories", [])
    if isinstance(categories, list):
        for cat in categories:
            cat_assets = cat.get("assets", [])
            if isinstance(cat_assets, list):
                for a in cat_assets:
                    if isinstance(a, str) and a:
                        assets.add(a)

    # 3. certificate profiles
    cert_profile = manifest.get("certificate_profile")
    if isinstance(cert_profile, dict):
        template_asset_ids = cert_profile.get("template_asset_ids", [])
        if isinstance(template_asset_ids, list):
            for t_id in template_asset_ids:
                if isinstance(t_id, dict):
                    versions = t_id.get("versions", [])
                    if isinstance(versions, list):
                        for v in versions:
                            if isinstance(v, dict):
                                filename = v.get("filename")
                                if filename:
                                    assets.add(filename)
    
    # 4. homepage video
    hp_video = manifest.get("homepage_video")
    if isinstance(hp_video, dict):
        video = hp_video.get("video")
        if video and isinstance(video, str) and "." in video:
            assets.add(video)

    return list(assets)
