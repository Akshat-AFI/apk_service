import os
import time
import shutil
import subprocess
from typing import Dict
from app.core.apk_config import settings

def build_apk(lang_id: str, draft: bool=False) -> Dict[str, str]:
    """
    Builds a React Native Android APK from the frontend project.
    - Builds 'assembleDevRelease' if draft=True
    - Builds 'assembleProductionRelease' if draft=False
    """

    android_dir = os.path.abspath(settings.ANDROID_PROJECT_DIR)
    output_dir = os.path.abspath(settings.APK_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)

    timestamp = int(time.time())
    variant = "dev" if draft else "production"
    gradle_task = f"assemble{variant.capitalize()}Release"
    print(f"🏗️ Building {variant.upper()}Release APK for {lang_id} ...")

    # Pick correct Gradle wrapper for platform
    gradlew = "gradlew.bat" if os.name == "nt" else "./gradlew"

    # 🧹 Clean previous build
    print("🧹 Running gradlew clean ...")
    subprocess.run([gradlew, "clean"], cwd=android_dir, shell=True, check=True)

    # 🏗️ Run actual Gradle build command
    # NOTE: We avoid capture_output/PIPE to prevent deadlocks on large Gradle logs (Windows buffer limit)
    try:
        subprocess.run(
            [gradlew, gradle_task],
            cwd=android_dir,
            shell=True,
            check=True
        )
    except subprocess.CalledProcessError:
        raise RuntimeError("Gradle build failed. Please check the terminal output for logs.")

    print("✅ Gradle build completed successfully!")

    # 🎯 Locate built APK path
    apk_path = os.path.join(android_dir, "app", "build", "outputs", "apk", variant, "release", f"app-{variant}-release.apk")

    if not os.path.exists(apk_path):
        raise FileNotFoundError(f"APK not found after build. Expected: {apk_path}")

    # 📦 Copy APK into service's /apks folder
    filename = f"app_{variant}_{timestamp}.apk"
    final_path = os.path.join(output_dir, filename)
    shutil.copy2(apk_path, final_path)

    print(f"✅ APK ready at: {final_path}")

    return {
        "filename": filename,
        "filepath": final_path,
        "createdAt": timestamp,
        "size": os.path.getsize(final_path),
        "draft": draft,
        "variant": variant
    }