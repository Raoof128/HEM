"""Configuration validation tests."""

from server.utils.config import ServiceConfig


def test_rate_limit_validation():
    """Negative rate limits should be rejected."""

    try:
        ServiceConfig(rate_limit_per_minute=-1)
    except ValueError as exc:  # noqa: PT017
        assert "rate_limit_per_minute" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("Negative rate limit should raise ValueError")


def test_env_override(monkeypatch):
    """Environment variables should override defaults."""

    monkeypatch.setenv("HEM_RATE_LIMIT_PER_MINUTE", "5")
    cfg = ServiceConfig()
    assert cfg.rate_limit_per_minute == 5
