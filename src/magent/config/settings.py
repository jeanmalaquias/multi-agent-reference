"""Per-agent, config-driven provider binding (ADR-003).

A single field per agent selects its LLM provider. Defaults to the offline
``mock`` provider so the vertical slice runs with zero secrets.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, overridable via env vars (prefix ``MAGENT_``)."""

    model_config = SettingsConfigDict(
        env_prefix="MAGENT_", env_file=".env", extra="ignore"
    )

    planner_provider: str = "mock"
    researcher_provider: str = "mock"
    writer_provider: str = "mock"
    critic_provider: str = "mock"

    max_revisions: int = 3

    def provider_for(self, agent: str) -> str:
        """Return the configured provider name for an agent role."""
        return getattr(self, f"{agent}_provider")


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
