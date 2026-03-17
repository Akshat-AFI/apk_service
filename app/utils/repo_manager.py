import os
import subprocess
from app.core.apk_config import settings

def clone_or_update_repo():
    """Clone the frontend repo if missing, otherwise pull the latest branch."""
    repo_dir = os.path.abspath(settings.FRONTEND_REPO_DIR)
    branch = settings.FRONTEND_REPO_BRANCH

    if not os.path.exists(os.path.join(repo_dir, ".git")):
        print(f"📦 Cloning frontend repo (branch {branch}) from {settings.FRONTEND_REPO_URL} ...")
        subprocess.run(
            ["git", "clone", "--branch", branch, "--single-branch", settings.FRONTEND_REPO_URL, repo_dir],
            check=True
        )
    else:
        print(f"🔄 Updating existing repo at {repo_dir} (ensuring branch {branch}) ...")
        subprocess.run(["git", "-C", repo_dir, "fetch", "origin", branch], check=True)
        subprocess.run(["git", "-C", repo_dir, "checkout", branch], check=True)
        subprocess.run(["git", "-C", repo_dir, "pull", "origin", branch], check=True)

    print("✅ Frontend repo ready:", repo_dir)
