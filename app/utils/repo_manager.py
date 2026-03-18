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
    
    # 📦 Install dependencies (required for Gradle plugins)
    node_modules_dir = os.path.join(repo_dir, "node_modules")
    package_json = os.path.join(repo_dir, "package.json")
    
    # Check if we need to install
    needs_install = not os.path.exists(node_modules_dir)
    if not needs_install and os.path.exists(package_json):
        # If package.json is newer than node_modules, we should install
        if os.path.getmtime(package_json) > os.path.getmtime(node_modules_dir):
            needs_install = True

    if needs_install:
        print(f"📦 Installing dependencies in {repo_dir} ...")
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        try:
            # Use 'npm install' instead of 'npm ci' to avoid full directory wipe which causes EPERM on Windows
            subprocess.run([npm_cmd, "install", "--no-audit", "--no-fund"], cwd=repo_dir, shell=True, check=True)
            print("✅ Dependencies installed.")
            # Touch node_modules to update its mtime
            os.utime(node_modules_dir, None)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error during npm install: {e}")
            print("💡 TIP: If you see EPERM errors, try stopping uvicorn and running the install manually once.")
            raise
    else:
        print("✅ Node modules are up to date.")
