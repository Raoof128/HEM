"""Simulated Homomorphic Encryption engine.

This module intentionally implements a *simulated* FHE scheme. Ciphertexts are structured
objects containing metadata, integrity tags, and obfuscated payloads, but they do not
provide real cryptographic confidentiality. The goal is to make encrypted workflows easy
to reason about without requiring heavy native dependencies.
"""

from __future__ import annotations

import base64
import json
import logging
import math
import secrets
import time
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from server.security.key_store import KEY_STORE

logger = logging.getLogger(__name__)


@dataclass
class Ciphertext:
    """Container representing encrypted data in the simulation."""

    key_id: str
    payload: list[float]
    noise: float
    created_at: float

    def serialize(self) -> str:
        """Serialize the ciphertext to a transport-safe string."""
        blob = {
            "key_id": self.key_id,
            "payload": self.payload,
            "noise": self.noise,
            "created_at": self.created_at,
        }
        encoded = json.dumps(blob).encode("utf-8")
        return base64.urlsafe_b64encode(encoded).decode("utf-8")

    @staticmethod
    def deserialize(data: str) -> Ciphertext:
        """Deserialize a ciphertext string back into a structured object."""
        decoded = base64.urlsafe_b64decode(data.encode("utf-8"))
        obj = json.loads(decoded.decode("utf-8"))
        return Ciphertext(
            key_id=obj["key_id"],
            payload=list(obj["payload"]),
            noise=float(obj["noise"]),
            created_at=float(obj["created_at"]),
        )


class SimulatedFHEEngine:
    """A lightweight, educational approximation of homomorphic encryption.

    Operations manipulate ciphertext payloads directly while tracking metadata.
    Integrity checks and key identifiers make it clear which key generated the data,
    but the payload remains visible. This is intentional for ease of demonstration and
    should not be used for sensitive information.
    """

    def __init__(self) -> None:
        self._public_key: str | None = None
        self._secret_key: str | None = None
        self._key_id: str | None = None

    @property
    def key_id(self) -> str:
        if not self._key_id:
            raise ValueError("Keys not generated. Call generate_keys first.")
        return self._key_id

    def generate_keys(self) -> dict[str, str]:
        """Generate a simulated keypair.

        Returns a public context that clients can safely use. The secret key is retained
        server-side only.
        """

        self._key_id = secrets.token_hex(8)
        self._public_key = secrets.token_urlsafe(16)
        self._secret_key = secrets.token_urlsafe(32)
        KEY_STORE.save_keys(self._key_id, self._public_key, self._secret_key)
        logger.info("Generated new simulated keypair", extra={"key_id": self._key_id})
        return {"key_id": self._key_id, "public_key": self._public_key}

    def encrypt(self, values: Sequence[float]) -> Ciphertext:
        """Encrypt numeric values into a ciphertext.

        The simulation injects random noise to mimic FHE ciphertext expansion and
        unpredictability. Values are cast to floats for consistent processing.
        """

        if self._public_key is None:
            raise ValueError("Keys not generated. Call generate_keys first.")
        if not values:
            raise ValueError("values cannot be empty")

        numeric = [float(v) for v in values]
        if not all(math.isfinite(value) for value in numeric):
            raise ValueError("values must be finite numeric types")
        noise = secrets.randbelow(100) / 10.0
        return Ciphertext(
            key_id=self.key_id,
            payload=[v + noise for v in numeric],
            noise=noise,
            created_at=time.time(),
        )

    def decrypt(self, ciphertext: Ciphertext) -> list[float]:
        """Decrypt a ciphertext back to plaintext values.

        Decryption removes the injected noise. This is only available on the server in
        real deployments. For simulations, it may be exposed conditionally.
        """

        if self._secret_key is None:
            raise ValueError("Secret key unavailable; generate keys first.")

        return [value - ciphertext.noise for value in ciphertext.payload]

    def _coerce_ciphertext(self, data: str | Ciphertext) -> Ciphertext:
        """Ensure a ciphertext object is available from serialized input."""

        if isinstance(data, Ciphertext):
            coerced = data
        else:
            if not data:
                raise ValueError("ciphertext is required")
            coerced = Ciphertext.deserialize(data)

        self._validate_ciphertext(coerced)
        return coerced

    def _validate_ciphertext(self, ciphertext: Ciphertext) -> None:
        """Verify ciphertext integrity and key ownership."""

        if self._key_id is None:
            raise ValueError("Keys not generated. Call generate_keys first.")
        if ciphertext.key_id != self._key_id:
            raise ValueError("ciphertext key does not match active key")
        if not ciphertext.payload:
            raise ValueError("ciphertext payload cannot be empty")

    def add(self, a: str | Ciphertext, b: str | Ciphertext) -> Ciphertext:
        """Homomorphic addition of two ciphertexts."""

        ct_a, ct_b = self._coerce_ciphertext(a), self._coerce_ciphertext(b)
        if len(ct_a.payload) != len(ct_b.payload):
            raise ValueError("payload sizes must match for addition")
        payload = list(np.add(ct_a.payload, ct_b.payload))
        noise = (ct_a.noise + ct_b.noise) / 2
        return Ciphertext(key_id=self.key_id, payload=payload, noise=noise, created_at=time.time())

    def mul(self, a: str | Ciphertext, b: str | Ciphertext) -> Ciphertext:
        """Homomorphic multiplication of two ciphertexts."""

        ct_a, ct_b = self._coerce_ciphertext(a), self._coerce_ciphertext(b)
        if len(ct_a.payload) != len(ct_b.payload):
            raise ValueError("payload sizes must match for multiplication")
        payload = list(np.multiply(ct_a.payload, ct_b.payload))
        noise = (ct_a.noise + ct_b.noise) + 1.0
        return Ciphertext(key_id=self.key_id, payload=payload, noise=noise, created_at=time.time())

    def scalar_mul(self, ciphertext: str | Ciphertext, scalar: float) -> Ciphertext:
        ct = self._coerce_ciphertext(ciphertext)
        payload = [value * scalar for value in ct.payload]
        return Ciphertext(
            key_id=self.key_id, payload=payload, noise=ct.noise + 0.2, created_at=time.time()
        )

    def dot(self, a: str | Ciphertext, b: str | Ciphertext) -> Ciphertext:
        ct_a, ct_b = self._coerce_ciphertext(a), self._coerce_ciphertext(b)
        if len(ct_a.payload) != len(ct_b.payload):
            raise ValueError("payload sizes must match for dot product")
        payload = [float(np.dot(ct_a.payload, ct_b.payload))]
        noise = ct_a.noise + ct_b.noise + 0.5
        return Ciphertext(key_id=self.key_id, payload=payload, noise=noise, created_at=time.time())

    def polynomial(self, ciphertext: str | Ciphertext, coefficients: Sequence[float]) -> Ciphertext:
        """Evaluate a polynomial on encrypted data using Horner's method."""

        ct = self._coerce_ciphertext(ciphertext)
        if not coefficients:
            raise ValueError("coefficients cannot be empty")
        result_payload = []
        for value in ct.payload:
            acc = 0.0
            for coeff in coefficients:
                acc = acc * value + coeff
            result_payload.append(acc)
        return Ciphertext(
            key_id=self.key_id, payload=result_payload, noise=ct.noise + 0.3, created_at=time.time()
        )

    def mean(self, ciphertext: str | Ciphertext) -> Ciphertext:
        ct = self._coerce_ciphertext(ciphertext)
        avg = float(np.mean(ct.payload))
        return Ciphertext(
            key_id=self.key_id, payload=[avg], noise=ct.noise + 0.1, created_at=time.time()
        )

    def linear_model(
        self, ciphertext: str | Ciphertext, weights: Sequence[float], bias: float = 0.0
    ) -> Ciphertext:
        ct = self._coerce_ciphertext(ciphertext)
        if len(weights) != len(ct.payload):
            raise ValueError("Weights and ciphertext dimensions do not match.")
        result = float(np.dot(ct.payload, np.array(weights)) + bias)
        return Ciphertext(
            key_id=self.key_id, payload=[result], noise=ct.noise + 0.4, created_at=time.time()
        )
