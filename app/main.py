from fastapi import FastAPI

from app.api.routes import quest, srs

app = FastAPI(title="German-Malayalam Quest API", version="0.1.0")

app.include_router(quest.router, prefix="/api/v1", tags=["quest"])
app.include_router(srs.router, prefix="/api/v1", tags=["srs"])


@app.get("/healthz")
def health():
    return {"status": "ok"}
