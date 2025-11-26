"""Key and encryption endpoints for the simulated HE microservice."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from server.he_engine import Ciphertext, SimulatedFHEEngine
from server.security.audit import log_event
from server.security.key_store import KEY_STORE
from server.utils.config import CONFIG

logger = logging.getLogger(__name__)

router = APIRouter(tags=["keys"])

engine: SimulatedFHEEngine | None = None


def init_engine(instance: SimulatedFHEEngine) -> None:
    """Initialize the module-level engine instance."""

    global engine
    engine = instance


def _get_engine() -> SimulatedFHEEngine:
    """Fetch the configured engine instance or raise when missing."""

    if engine is None:
        raise RuntimeError("Engine not initialized")
    return engine


class EncryptRequest(BaseModel):
    values: list[float] = Field(description="Plaintext numeric values to encrypt")

    @field_validator("values")
    @classmethod
    def validate_values(cls, values: list[float]) -> list[float]:
        if len(values) == 0:
            raise ValueError("values cannot be empty")
        return values


class DecryptRequest(BaseModel):
    ciphertext: str = Field(description="Serialized ciphertext produced by /encrypt")

    @field_validator("ciphertext")
    @classmethod
    def validate_ciphertext(cls, value: str) -> str:
        if not value:
            raise ValueError("ciphertext must be provided")
        return value


@router.post("/keys/generate")
def generate_keys() -> dict:
    """Generate and persist simulated keys using the key store."""

    eng = _get_engine()
    generated = eng.generate_keys()
    log_event("keys.generated", {"key_id": generated["key_id"]})
    return generated


@router.get("/keys/public")
def get_public_key() -> dict:
    """Return the public key material for the active key id."""

    eng = _get_engine()
    public_key = KEY_STORE.get_public_key(eng.key_id) or "SIMULATED_PUBLIC"
    return {"key_id": eng.key_id, "public_key": public_key}


@router.post("/encrypt")
def encrypt(request: EncryptRequest) -> dict:
    """Encrypt numeric values using the simulated engine."""

    eng = _get_engine()
    try:
        ciphertext = eng.encrypt(request.values)
        log_event("encrypt", {"key_id": ciphertext.key_id, "length": len(request.values)})
        return {"ciphertext": ciphertext.serialize()}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Encryption failed", exc_info=exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/decrypt")
def decrypt(request: DecryptRequest) -> dict:
    """Decrypt ciphertext when simulation mode allows it."""

    eng = _get_engine()
    if not CONFIG.enable_simulated_decrypt:
        raise HTTPException(status_code=403, detail="Decrypt endpoint disabled")
    try:
        decrypted = eng.decrypt(Ciphertext.deserialize(request.ciphertext))
        log_event("decrypt", {"key_id": eng.key_id, "length": len(decrypted)})
        return {"values": decrypted}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Decryption failed", exc_info=exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
