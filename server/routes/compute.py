"""Computation endpoints for simulated homomorphic operations."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from server.he_engine import Ciphertext, SimulatedFHEEngine
from server.security.audit import log_event

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compute", tags=["compute"])


class CiphertextPayload(BaseModel):
    ciphertext: str = Field(description="Serialized ciphertext")

    @field_validator("ciphertext")
    @classmethod
    def validate_ciphertext(cls, value: str) -> str:
        if not value:
            raise ValueError("ciphertext must be provided")
        return value


class PolynomialRequest(CiphertextPayload):
    coefficients: list[float] = Field(description="Polynomial coefficients")

    @field_validator("coefficients")
    @classmethod
    def validate_coefficients(cls, coeffs: Sequence[float]) -> Sequence[float]:
        if len(coeffs) == 0:
            raise ValueError("coefficients cannot be empty")
        return coeffs


class LinearModelRequest(CiphertextPayload):
    weights: list[float] = Field(description="Model weights")
    bias: float = Field(default=0.0, description="Model bias")

    @field_validator("weights")
    @classmethod
    def validate_weights(cls, weights: Sequence[float]) -> Sequence[float]:
        if len(weights) == 0:
            raise ValueError("weights cannot be empty")
        return weights


class BinaryOpRequest(BaseModel):
    a: str = Field(description="Left ciphertext")
    b: str = Field(description="Right ciphertext")

    @field_validator("a", "b")
    @classmethod
    def validate_ciphertexts(cls, value: str) -> str:
        if not value:
            raise ValueError("ciphertext must be provided")
        return value


engine: SimulatedFHEEngine | None = None


def init_engine(instance: SimulatedFHEEngine) -> None:
    """Initialize the module-level engine instance."""

    global engine
    engine = instance


def _get_engine() -> SimulatedFHEEngine:
    """Fetch the configured engine or raise a runtime error."""

    if engine is None:
        raise RuntimeError("Engine not initialized")
    return engine


@router.post("/add")
def add(request: BinaryOpRequest) -> dict:
    """Add two ciphertexts."""

    eng = _get_engine()
    try:
        result = eng.add(request.a, request.b).serialize()
        log_event("compute.add", {"key_id": eng.key_id})
        return {"ciphertext": result}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Add operation failed", exc_info=exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/mul")
def multiply(request: BinaryOpRequest) -> dict:
    """Multiply two ciphertexts element-wise."""

    eng = _get_engine()
    try:
        result = eng.mul(request.a, request.b).serialize()
        log_event("compute.mul", {"key_id": eng.key_id})
        return {"ciphertext": result}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Multiplication failed", exc_info=exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/dot")
def dot(request: BinaryOpRequest) -> dict:
    """Compute dot product between two ciphertext vectors."""

    eng = _get_engine()
    try:
        result = eng.dot(request.a, request.b).serialize()
        log_event("compute.dot", {"key_id": eng.key_id})
        return {"ciphertext": result}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Dot product failed", exc_info=exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/polynomial")
def polynomial(request: PolynomialRequest) -> dict:
    eng = _get_engine()
    try:
        ciphertext = Ciphertext.deserialize(request.ciphertext)
        result = eng.polynomial(ciphertext, request.coefficients).serialize()
        log_event(
            "compute.polynomial", {"key_id": eng.key_id, "degree": len(request.coefficients) - 1}
        )
        return {"ciphertext": result}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Polynomial evaluation failed", exc_info=exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/mean")
def mean(request: CiphertextPayload) -> dict:
    eng = _get_engine()
    try:
        ciphertext = Ciphertext.deserialize(request.ciphertext)
        result = eng.mean(ciphertext).serialize()
        log_event("compute.mean", {"key_id": eng.key_id})
        return {"ciphertext": result}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Mean computation failed", exc_info=exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/linear")
def linear_model(request: LinearModelRequest) -> dict:
    eng = _get_engine()
    try:
        ciphertext = Ciphertext.deserialize(request.ciphertext)
        result = eng.linear_model(
            ciphertext, weights=request.weights, bias=request.bias
        ).serialize()
        log_event("compute.linear", {"key_id": eng.key_id})
        return {"ciphertext": result}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Linear model computation failed", exc_info=exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
