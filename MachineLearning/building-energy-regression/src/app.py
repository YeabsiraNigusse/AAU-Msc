"""Serve the fitted building energy model over local HTTP."""

import json
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter

import joblib
import pandas as pd
from fastapi import FastAPI, Request
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__" and not __package__:
    # The saved pipeline references src.features when joblib loads it.
    sys.path.insert(0, str(PROJECT_ROOT))

from src.design import BuildingDesign
from src.features import FEATURES, TARGETS

ARTIFACT = PROJECT_ROOT / "artifacts" / "model.joblib"
logger = logging.getLogger("uvicorn.error")


class LoadPrediction(BaseModel):
    heating_load: float
    cooling_load: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.bundle = joblib.load(ARTIFACT)
    yield


app = FastAPI(title="Building Energy Efficiency", lifespan=lifespan)


@app.middleware("http")
async def log_request(request: Request, call_next):
    start = perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        record = {
            "path": request.url.path,
            "status": status,
            "latency_ms": round(1000 * (perf_counter() - start), 2),
            "outside_training_range": getattr(request.state, "outside_range", []),
        }
        logger.info("request_metrics %s", json.dumps(record))


@app.get("/health")
def health():
    return {"status": "ready"}


@app.post("/predict")
def predict(design: BuildingDesign, request: Request) -> LoadPrediction:
    values = design.model_dump()
    bundle = request.app.state.bundle
    request.state.outside_range = [
        field for field, (low, high) in bundle["training_bounds"].items()
        if not low <= values[field] <= high
    ]
    frame = pd.DataFrame([values], columns=FEATURES)
    prediction = bundle["pipeline"].predict(frame)[0]
    return LoadPrediction(**dict(zip(TARGETS, prediction.tolist())))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
