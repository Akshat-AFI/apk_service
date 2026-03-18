from fastapi import APIRouter, Query, HTTPException
import os
from app.services.apk_service import generate_apk
from app.utils.apk_consts import read_apk_list
from app.core.apk_config import settings

router = APIRouter(prefix="/apk", tags=["APK"])

@router.post("/generate")
async def generate(langId: str = Query(...), draft: bool = Query(False)):
    try:
        result = await generate_apk(langId, draft)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_apks():
    return read_apk_list()

@router.get("/status")
async def status():
    return {"status": "BUSY" if os.path.exists(settings.LOCK_FILE) else "READY"}
