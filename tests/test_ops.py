from server.he_engine import SimulatedFHEEngine


def setup_engine() -> SimulatedFHEEngine:
    """Create a fresh engine with generated keys."""

    engine = SimulatedFHEEngine()
    engine.generate_keys()
    return engine


def test_add_operation():
    """Addition should combine payloads and average noise."""

    engine = setup_engine()
    a = engine.encrypt([1, 2])
    b = engine.encrypt([3, 4])
    result = engine.decrypt(engine.add(a, b))
    expected = [
        (1 + 3) + (a.noise + b.noise) / 2,
        (2 + 4) + (a.noise + b.noise) / 2,
    ]
    assert all(abs(r - e) < 1e-6 for r, e in zip(result, expected))


def test_dot_operation():
    """Dot product should reduce to a single-element payload."""

    engine = setup_engine()
    a = engine.encrypt([1, 2, 3])
    b = engine.encrypt([4, 5, 6])
    result = engine.decrypt(engine.dot(a, b))
    assert len(result) == 1


def test_polynomial_operation():
    """Polynomial evaluation should produce finite results."""

    engine = setup_engine()
    ct = engine.encrypt([2])
    coefficients = [1, 0, 2]  # 2*x^2 + 1
    result = engine.decrypt(engine.polynomial(ct, coefficients))
    assert result[0] > 0


def test_reject_mismatched_payload_sizes():
    """Engine should reject mismatched vector sizes for binary ops."""

    engine = setup_engine()
    ct_small = engine.encrypt([1, 2])
    ct_large = engine.encrypt([1, 2, 3])
    try:
        engine.add(ct_small, ct_large)
    except ValueError as exc:  # noqa: PT017
        assert "payload sizes must match" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected ValueError for mismatched payload sizes")


def test_reject_cross_key_operations():
    """Cross-key operations must be rejected for safety."""

    engine_one = setup_engine()
    engine_two = setup_engine()

    ciphertext_one = engine_one.encrypt([1, 2, 3])
    ciphertext_two = engine_two.encrypt([4, 5, 6])

    try:
        engine_one.add(ciphertext_one, ciphertext_two)
    except ValueError as exc:  # noqa: PT017
        assert "ciphertext key does not match" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected ValueError for key mismatch")
