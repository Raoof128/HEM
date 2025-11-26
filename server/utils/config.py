"""Configuration utilities for the microservice.

The service uses :class:`pydantic.BaseSettings` to allow environment-driven overrides
without requiring an external configuration service. Defaults remain safe for local
development while enabling production deployments to tighten controls via environment
variables (e.g., disabling simulated decrypt or reducing rate limits).
"""

from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseSettings):
    """Runtime configuration for the service.

    In a production system this would be loaded from environment variables or a
    configuration service. For the educational microservice we provide sensible defaults
    and allow optional overrides.
    """

    service_name: str = Field(default="HEM Microservice", description="Human-friendly service name")
    rate_limit_per_minute: int = Field(
        default=120, description="Soft rate-limit for requests per minute"
    )
    enable_simulated_decrypt: bool = Field(
        default=True,
        description=(
            "Allow server-side decrypt endpoint for demonstrations. This should be disabled in "
            "production deployments."
        ),
    )
    audit_log_path: str = Field(default="logs/audit.log", description="Path to audit log file")

    @field_validator("rate_limit_per_minute")
    @classmethod
    def validate_rate_limit(cls, value: int) -> int:
        """Ensure rate limits are non-negative."""

        if value < 0:
            raise ValueError("rate_limit_per_minute cannot be negative")
        return value

    model_config = SettingsConfigDict(
        env_prefix="HEM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


CONFIG = ServiceConfig()
