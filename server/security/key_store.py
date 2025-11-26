"""Key store simulating secure key management."""

from __future__ import annotations

import threading


class KeyStore:
    """Thread-safe in-memory key store.

    In production this would wrap an HSM or cloud KMS. Here we only persist keys for the
    lifetime of the process and avoid exposing secrets through the API layer.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._public_keys: dict[str, str] = {}
        self._secret_keys: dict[str, str] = {}

    def save_keys(self, key_id: str, public_key: str, secret_key: str) -> None:
        """Persist keys in-memory for the provided key identifier."""

        with self._lock:
            self._public_keys[key_id] = public_key
            self._secret_keys[key_id] = secret_key

    def get_public_key(self, key_id: str) -> str | None:
        """Retrieve a public key for the supplied identifier."""

        with self._lock:
            return self._public_keys.get(key_id)

    def has_secret(self, key_id: str) -> bool:
        """Return True when a secret key exists for the given identifier."""

        with self._lock:
            return key_id in self._secret_keys

    def clear(self) -> None:
        """Remove all stored keys."""

        with self._lock:
            self._public_keys.clear()
            self._secret_keys.clear()


KEY_STORE = KeyStore()
