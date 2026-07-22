from pydantic_settings import BaseSettings
from pydantic import Field

class APKSettings(BaseSettings):
    LME_BASE_URL: str = Field("http://74.224.97.26:8004", description="LME API base URL")
    LME_AUTH_TOKEN: str = Field("", description="Internal security access token for LME API")
    GITHUB_USER: str = Field("Akshat-AFI", description="GitHub username for private repo access")
    GITHUB_PAT: str = Field("", description="GitHub Personal Access Token")
    APK_OUTPUT_DIR: str = Field("apks", description="Output folder for generated APKs")
    CONTENT_DIR: str = Field("content", description="Where language content & assets are downloaded")
    APK_LIST_FILE: str = Field("apks_list.json", description="APK metadata list")
    LOCK_FILE: str = Field("generation.lock", description="Lock file")
    ANDROID_PROJECT_DIR: str = Field("../android", description="Path to your React Native android project")
    GRADLE_JAVA_HOME: str = Field(
        r"C:\Program Files\Android\Android Studio\jbr",
        description="JDK 17+ home used for the Gradle build (RN/AGP require Java 11+). Set to '' to use the ambient JAVA_HOME/PATH.",
    )
    GRADLE_USER_HOME: str = Field(
        ".gradle-home",
        description="Dedicated Gradle user home for the build. Its gradle.properties overrides the frontend's (e.g. heap), pull-safe.",
    )
    GRADLE_MAX_HEAP: str = Field(
        "4g",
        description="Max JVM heap for the Gradle daemon (-Xmx). The frontend pins 16g which OOMs on <16GB machines.",
    )
    AZURE_APK_BASE_URL: str = Field("https://sdacms.blob.core.windows.net/apk/", description="Azure Blob storage base URL")
    AZURE_APK_CONTAINER: str = Field("apk", description="Azure Blob container name for uploaded APKs")
    AZURE_STORAGE_CONNECTION_STRING: str = Field("", description="Azure Storage connection string (required when UPLOAD_APK_TO_AZURE=True)")
    ANDROID_ASSETS_BASE: str = "frontend_app/assets"
    UPLOAD_APK_TO_AZURE: bool = Field(False, description="Whether to upload APK to Azure")
    FRONTEND_REPO_URL: str = Field("https://github.com/maternity-foundation-production/sdp-app.git", description="Frontend repository URL")
    FRONTEND_REPO_BRANCH: str = "feat/apk_service"
    FRONTEND_REPO_DIR: str = "frontend_app"
    ANDROID_PROJECT_DIR: str = "frontend_app/android"
    MANIFEST_OUTPUT_DIR: str = "frontend_app/android/app/src/main/assets/bundled"
    ASSETS_OUTPUT_DIR: str = "frontend_app/android/app/src/main/assets/bundled/assets"

    class Config:
        env_file = ".env"

settings = APKSettings()
