"""FastAPI entrypoint for the Homomorphic Encryption Microservice."""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from server.he_engine import SimulatedFHEEngine
from server.routes import compute, debug, keys
from server.security.audit import log_event
from server.utils.config import CONFIG


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[override]
    """Application lifespan hooks for startup/shutdown events."""

    log_event("startup", {"key_id": _engine.key_id})
    yield


logger = logging.getLogger(__name__)


app = FastAPI(title="Homomorphic Encryption Microservice", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_engine = SimulatedFHEEngine()
_engine.generate_keys()
compute.init_engine(_engine)
keys.init_engine(_engine)


def rate_limiter() -> None:
    """Naive in-memory rate limiter for demonstration purposes."""

    if CONFIG.rate_limit_per_minute <= 0:
        return
    now = int(time.time())
    window = now // 60
    key = f"window:{window}"
    count = rate_limits.get(key, 0)
    if count >= CONFIG.rate_limit_per_minute:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    rate_limits[key] = count + 1


rate_limits: dict[str, int] = {}


@app.middleware("http")
async def audit_requests(request: Request, call_next):  # type: ignore[override]
    """Record request metrics and propagate responses."""

    start = time.time()
    response = await call_next(request)
    elapsed_ms = int((time.time() - start) * 1000)
    log_event(
        "http.access",
        {
            "path": request.url.path,
            "method": request.method,
            "status": response.status_code,
            "elapsed_ms": elapsed_ms,
        },
    )
    return response


@app.get("/")
def root() -> dict[str, Any]:
    """Basic landing endpoint exposing service name and key identifier."""

    try:
        key_identifier = _engine.key_id
    except ValueError:
        logger.warning("Key identifier unavailable; ensure keys are generated")
        key_identifier = None
    return {"message": CONFIG.service_name, "key_id": key_identifier}


app.include_router(keys.router, dependencies=[Depends(rate_limiter)])
app.include_router(compute.router, dependencies=[Depends(rate_limiter)])
app.include_router(debug.router)
