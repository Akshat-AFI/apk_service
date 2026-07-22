import sys

# Force UTF-8 stdout/stderr so emoji log lines don't crash on Windows (cp1252) consoles.
for _stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(_stream, "reconfigure", None)
    if reconfigure:
        reconfigure(encoding="utf-8")

from fastapi import FastAPI
from app.routers import apk

app = FastAPI(title="APK Builder Service", version="1.0.0")
app.include_router(apk.router)

@app.get("/")
def root():
    return {"message": "Welcome to LME APK Builder Service"}
