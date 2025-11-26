"""API integration tests for FastAPI app."""

from __future__ import annotations

from fastapi.testclient import TestClient

from server.main import app

client = TestClient(app)


def test_health_endpoint():
    """Health endpoint should return ok."""

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_encrypt_add_flow():
    """Ensure encrypt → add → decrypt round-trip behaves as expected."""

    client.post("/keys/generate")
    encrypt_resp = client.post("/encrypt", json={"values": [1, 2, 3]})
    assert encrypt_resp.status_code == 200
    ciphertext = encrypt_resp.json()["ciphertext"]

    add_resp = client.post("/compute/add", json={"a": ciphertext, "b": ciphertext})
    assert add_resp.status_code == 200
    added_ciphertext = add_resp.json()["ciphertext"]

    decrypt_resp = client.post("/decrypt", json={"ciphertext": added_ciphertext})
    assert decrypt_resp.status_code == 200
    values = decrypt_resp.json()["values"]
    assert len(values) == 3
