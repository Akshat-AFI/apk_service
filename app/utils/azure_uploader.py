from typing import Optional
from app.core.apk_config import settings


def upload_apk_to_azure(local_path: str, blob_name: str) -> Optional[str]:
    """Upload a built APK to the Azure 'apk' container.

    Returns the public blob URL on success, or None when uploads are disabled.
    Raises if uploading is enabled but the upload fails (e.g. bad/missing
    connection string) so misconfiguration surfaces loudly.
    """
    if not settings.UPLOAD_APK_TO_AZURE:
        return None

    conn = settings.AZURE_STORAGE_CONNECTION_STRING
    if not conn:
        raise RuntimeError(
            "UPLOAD_APK_TO_AZURE is True but AZURE_STORAGE_CONNECTION_STRING is not set."
        )

    # Imported lazily so the dependency is only required when uploads are enabled.
    from azure.storage.blob import BlobServiceClient, ContentSettings

    service = BlobServiceClient.from_connection_string(conn)
    blob_client = service.get_blob_client(
        container=settings.AZURE_APK_CONTAINER, blob=blob_name
    )

    print(f"☁️ Uploading APK to Azure container '{settings.AZURE_APK_CONTAINER}' ...")
    with open(local_path, "rb") as f:
        blob_client.upload_blob(
            f,
            overwrite=True,
            content_settings=ContentSettings(
                content_type="application/vnd.android.package-archive"
            ),
        )

    url = f"{settings.AZURE_APK_BASE_URL.rstrip('/')}/{blob_name}"
    print(f"✅ Uploaded APK to Azure: {url}")
    return url
