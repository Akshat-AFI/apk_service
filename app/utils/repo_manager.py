import os
import subprocess
from app.core.apk_config import settings

def clone_or_update_repo():
    """Clone the frontend repo if missing, otherwise pull the latest branch."""
    repo_dir = os.path.abspath(settings.FRONTEND_REPO_DIR)
    branch = settings.FRONTEND_REPO_BRANCH

    # Prepare authenticated URL if PAT is available
    repo_url = settings.FRONTEND_REPO_URL
    if settings.GITHUB_PAT and settings.GITHUB_USER:
        if "https://" in repo_url:
            base_url = repo_url.replace("https://", "")
            repo_url = f"https://{settings.GITHUB_USER}:{settings.GITHUB_PAT}@{base_url}"

    if not os.path.exists(os.path.join(repo_dir, ".git")):
        print(f"📦 Cloning frontend repo (branch {branch}) ...")
        subprocess.run(
            ["git", "clone", "--branch", branch, "--single-branch", repo_url, repo_dir],
            check=True
        )
    else:
        print(f"🔄 Updating existing repo at {repo_dir} (ensuring branch {branch}) ...")
        subprocess.run(["git", "-C", repo_dir, "fetch", "origin", branch], check=True)
        subprocess.run(["git", "-C", repo_dir, "checkout", branch], check=True)
        subprocess.run(["git", "-C", repo_dir, "pull", "origin", branch], check=True)

    print("✅ Frontend repo ready:", repo_dir)
