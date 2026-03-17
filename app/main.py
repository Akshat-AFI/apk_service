from fastapi import FastAPI
from app.routers import apk

app = FastAPI(title="APK Builder Service", version="1.0.0")
app.include_router(apk.router)

@app.get("/")
def root():
    return {"message": "Welcome to LME APK Builder Service"}
