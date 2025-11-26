from server.he_engine import SimulatedFHEEngine


def test_encrypt_decrypt_round_trip():
    """Simulated encryption should be reversible with decrypt."""

    engine = SimulatedFHEEngine()
    engine.generate_keys()
    plaintext = [1.0, 2.0, 3.0]
    ciphertext = engine.encrypt(plaintext)
    decrypted = engine.decrypt(ciphertext)
    assert all(abs(p - d) < 1e-6 for p, d in zip(plaintext, decrypted))


def test_ciphertext_serialization():
    """Ciphertext should serialize and deserialize consistently."""

    engine = SimulatedFHEEngine()
    engine.generate_keys()
    ct = engine.encrypt([4.2, 5.1])
    encoded = ct.serialize()
    decoded = engine.decrypt(engine._coerce_ciphertext(encoded))  # pylint: disable=protected-access
    assert len(decoded) == 2


def test_encrypt_rejects_non_finite_values():
    """Engine should reject non-finite values during encryption."""

    engine = SimulatedFHEEngine()
    engine.generate_keys()
    try:
        engine.encrypt([float("nan"), 1.0])
    except ValueError as exc:  # noqa: PT017
        assert "finite" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected failure for non-finite values")
