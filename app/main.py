from fastapi import FastAPI
from app.api.v1.router import router as v1_router
from sqlalchemy import text
from app.db.session import SessionLocal  # adjust import if your SessionLocal lives elsewhere

app = FastAPI(title="Decision Room API", version="0.1.0")
app.include_router(v1_router)

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

@app.get("/ready", tags=["Health"])
def ready():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception:
        # don't leak internal error details here
        return {"status": "degraded", "db": "down"}
    finally:
        try:
            db.close()
        except Exception:
            pass
