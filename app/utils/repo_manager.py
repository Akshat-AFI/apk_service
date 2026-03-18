import os
import subprocess
import hashlib
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
    package_lock = os.path.join(repo_dir, "package-lock.json")
    package_json = os.path.join(repo_dir, "package.json")
    checksum_file = os.path.join(repo_dir, ".package_checksum")
    
    # Calculate current checksum of package-lock.json (or package.json if lock missing)
    target_file = package_lock if os.path.exists(package_lock) else package_json
    current_checksum = ""
    if os.path.exists(target_file):
        with open(target_file, "rb") as f:
            current_checksum = hashlib.md5(f.read()).hexdigest()

    stored_checksum = ""
    if os.path.exists(checksum_file):
        with open(checksum_file, "r") as f:
            stored_checksum = f.read().strip()

    # Check if we need to install
    needs_install = not os.path.exists(node_modules_dir) or current_checksum != stored_checksum

    if needs_install:
        print(f"📦 Dependencies out of date or missing. Installing in {repo_dir} ...")
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        try:
            # Use 'npm install' with --prefer-offline for speed
            subprocess.run([npm_cmd, "install", "--no-audit", "--no-fund", "--prefer-offline"], cwd=repo_dir, shell=True, check=True)
            print("✅ Dependencies installed.")
            # Update stored checksum
            with open(checksum_file, "w") as f:
                f.write(current_checksum)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error during npm install: {e}")
            print("💡 TIP: If you see EPERM errors, try stopping the service and running 'npm install' manually once.")
            raise
    else:
        print("✅ Node modules are up to date (checksum matched).")
