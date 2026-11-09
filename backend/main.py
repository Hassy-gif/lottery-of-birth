"""Lottery of Birth API."""
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from simulator import DATA, SEED_PATTERN, TOTAL_BIRTHS, new_seed, simulate

app = FastAPI(title="Lottery of Birth API")

# Only our own frontend may call this API from a browser.
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET"])


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/born")
def born():
    """Roll a brand-new life."""
    return simulate(new_seed())


@app.get("/api/life/{seed}")
def life(seed: str):
    """Replay a shared life from its ID."""
    if not SEED_PATTERN.fullmatch(seed):
        raise HTTPException(status_code=400, detail="Invalid life ID")
    return simulate(seed)


@app.get("/api/stats")
def stats():
    return {
        "countries": len(DATA),
        "births_per_year": TOTAL_BIRTHS,
        "most_likely": [
            {"name": c["name"], "percent": round(c["births_per_year"] / TOTAL_BIRTHS * 100, 1)}
            for c in DATA[:10]
        ],
    }
