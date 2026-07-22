import os
import time
import shutil
import subprocess
from typing import Any, Dict
from app.core.apk_config import settings
from app.utils.azure_uploader import upload_apk_to_azure

def build_apk(lang_id: str, lang_version: str, draft: bool=False) -> Dict[str, Any]:
    """
    Builds a React Native Android APK from the frontend project.
    - Builds 'assembleDevRelease' if draft=True
    - Builds 'assembleProductionRelease' if draft=False

    The Gradle build itself is identical for draft/published; only the variant
    and the saved filename/metadata differ.
    """

    android_dir = os.path.abspath(settings.ANDROID_PROJECT_DIR)
    output_dir = os.path.abspath(settings.APK_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)

    timestamp = int(time.time())
    variant = "dev" if draft else "production"
    build_type = "draft" if draft else "published"
    gradle_task = f"assemble{variant.capitalize()}Release"
    print(f"🏗️ Building {variant.upper()}Release APK for {lang_id} ...")

    # Pick correct Gradle wrapper for platform
    gradlew = "gradlew.bat" if os.name == "nt" else "./gradlew"

    # ☕ Force a JDK 17+ for Gradle (RN/AGP won't build on Java 8). The Gradle
    # subprocess inherits this env, so it works regardless of the shell that
    # launched the service. Set GRADLE_JAVA_HOME="" to fall back to ambient JAVA_HOME.
    build_env = os.environ.copy()
    java_home = settings.GRADLE_JAVA_HOME
    if java_home:
        if not os.path.isdir(java_home):
            raise RuntimeError(
                f"GRADLE_JAVA_HOME does not exist: {java_home}. "
                "Point it at a JDK 17+ install (e.g. Android Studio's bundled JBR)."
            )
        build_env["JAVA_HOME"] = java_home
        build_env["PATH"] = os.path.join(java_home, "bin") + os.pathsep + build_env.get("PATH", "")
        print(f"☕ Using JAVA_HOME for Gradle: {java_home}")

    # 🧠 Cap the Gradle daemon heap via a dedicated GRADLE_USER_HOME. The frontend
    # pins -Xmx16g which OOMs on <16GB machines; a gradle.properties here overrides
    # the project's, and survives the git pull in repo_manager.
    gradle_home = os.path.abspath(settings.GRADLE_USER_HOME)
    os.makedirs(gradle_home, exist_ok=True)
    with open(os.path.join(gradle_home, "gradle.properties"), "w", encoding="utf-8") as f:
        f.write(f"org.gradle.jvmargs=-Xmx{settings.GRADLE_MAX_HEAP} -XX:MaxMetaspaceSize=512m\n")
    build_env["GRADLE_USER_HOME"] = gradle_home
    print(f"🧠 Gradle heap capped to -Xmx{settings.GRADLE_MAX_HEAP} (GRADLE_USER_HOME={gradle_home})")

    # 🧹 Clean previous build
    subprocess.run([gradlew, "clean"], cwd=android_dir, shell=True, check=False, env=build_env)

    # 🏗️ Run actual Gradle build command
    # NOTE: We avoid capture_output/PIPE to prevent deadlocks on large Gradle logs (Windows buffer limit)
    try:
        subprocess.run(
            [gradlew, gradle_task],
            cwd=android_dir,
            shell=True,
            check=True,
            env=build_env
        )
    except subprocess.CalledProcessError:
        raise RuntimeError("Gradle build failed. Please check the terminal output for logs.")

    print("✅ Gradle build completed successfully!")

    # 🎯 Locate built APK path
    apk_path = os.path.join(android_dir, "app", "build", "outputs", "apk", variant, "release", f"app-{variant}-release.apk")

    if not os.path.exists(apk_path):
        raise FileNotFoundError(f"APK not found after build. Expected: {apk_path}")

    # 📦 Copy APK into service's /apks folder
    filename = f"{lang_id}_{lang_version}_{build_type}_{timestamp}.apk"
    final_path = os.path.join(output_dir, filename)
    shutil.copy2(apk_path, final_path)

    print(f"✅ APK ready at: {final_path}")

    # ☁️ Optionally upload to Azure (no-op unless UPLOAD_APK_TO_AZURE=True)
    azure_url = upload_apk_to_azure(final_path, filename)

    meta: Dict[str, Any] = {
        "filename": filename,
        "createdAt": timestamp,
        "size": os.path.getsize(final_path),
        "draft": draft,
        "lang_version": lang_version,
    }
    if azure_url:
        meta["azure_url"] = azure_url
    return meta