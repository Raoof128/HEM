"""Python SDK for the Homomorphic Encryption Microservice."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import requests


class HEMClient:
    """Minimal client for interacting with the microservice."""

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        """Create a client targeting the given base URL."""

        self.base_url = base_url.rstrip("/")

    def _handle_response(self, response: requests.Response) -> dict[str, Any]:
        """Return JSON payload or raise detailed error."""

        try:
            response.raise_for_status()
        except requests.HTTPError as error:  # pragma: no cover - thin wrapper
            detail = response.text
            raise RuntimeError(f"Request failed: {response.status_code} {detail}") from error
        return response.json()

    def health(self) -> dict[str, Any]:
        """Check service health."""

        response = requests.get(f"{self.base_url}/health", timeout=5)
        return self._handle_response(response)

    def generate_keys(self) -> dict[str, str]:
        """Request new simulated key material."""

        response = requests.post(f"{self.base_url}/keys/generate", timeout=5)
        return self._handle_response(response)

    def encrypt(self, values: Sequence[float]) -> str:
        """Encrypt plaintext values via the API."""

        response = requests.post(
            f"{self.base_url}/encrypt", json={"values": list(values)}, timeout=5
        )
        return self._handle_response(response)["ciphertext"]

    def decrypt(self, ciphertext: str) -> list[float]:
        """Decrypt ciphertext via the API (demo-only endpoint)."""

        response = requests.post(
            f"{self.base_url}/decrypt", json={"ciphertext": ciphertext}, timeout=5
        )
        return self._handle_response(response)["values"]

    def add(self, a: str, b: str) -> str:
        """Add two ciphertexts element-wise."""

        response = requests.post(f"{self.base_url}/compute/add", json={"a": a, "b": b}, timeout=5)
        return self._handle_response(response)["ciphertext"]

    def mul(self, a: str, b: str) -> str:
        """Multiply two ciphertexts element-wise."""

        response = requests.post(f"{self.base_url}/compute/mul", json={"a": a, "b": b}, timeout=5)
        return self._handle_response(response)["ciphertext"]

    def dot(self, a: str, b: str) -> str:
        """Compute dot product over two ciphertext vectors."""

        response = requests.post(f"{self.base_url}/compute/dot", json={"a": a, "b": b}, timeout=5)
        return self._handle_response(response)["ciphertext"]

    def polynomial(self, ciphertext: str, coefficients: Sequence[float]) -> str:
        """Evaluate a polynomial against ciphertext payloads."""

        response = requests.post(
            f"{self.base_url}/compute/polynomial",
            json={"ciphertext": ciphertext, "coefficients": list(coefficients)},
            timeout=5,
        )
        return self._handle_response(response)["ciphertext"]

    def mean(self, ciphertext: str) -> str:
        """Compute the arithmetic mean of ciphertext payloads."""

        response = requests.post(
            f"{self.base_url}/compute/mean", json={"ciphertext": ciphertext}, timeout=5
        )
        return self._handle_response(response)["ciphertext"]

    def linear_model(self, ciphertext: str, weights: Sequence[float], bias: float = 0.0) -> str:
        """Run a simple linear model on ciphertext payloads."""

        response = requests.post(
            f"{self.base_url}/compute/linear",
            json={"ciphertext": ciphertext, "weights": list(weights), "bias": bias},
            timeout=5,
        )
        return self._handle_response(response)["ciphertext"]
