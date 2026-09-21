"""Runtime configuration, read from environment variables."""

from __future__ import annotations

import math
import os
from collections.abc import Mapping
from dataclasses import dataclass

DEFAULT_BASE_URL = "https://openapi.growatt.com"

#: Regional OpenAPI hosts documented by Growatt.
REGIONS: dict[str, str] = {
    "global": DEFAULT_BASE_URL,
    "eu": DEFAULT_BASE_URL,
    "cn": "https://openapi-cn.growatt.com",
    "us": "https://openapi-us.growatt.com",
}

HOW_TO_GET_ACCESS = "Get your token in the ShinePhone app: Me > tap your username > API Token."
TRUE_VALUES = {"1", "true", "yes", "on"}


class ConfigError(ValueError):
    """Raised when the environment does not describe a usable configuration."""


@dataclass(frozen=True)
class Settings:
    token: str
    base_url: str = DEFAULT_BASE_URL
    timeout: float = 30.0
    read_only: bool = False


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Build :class:`Settings` from ``GROWATT_*`` environment variables.

    ``GROWATT_TOKEN`` is required. ``GROWATT_BASE_URL`` overrides the API host directly (https only);
    otherwise ``GROWATT_REGION`` (``global``, ``eu``, ``cn`` or ``us``) selects one of the documented
    regional hosts. ``GROWATT_TIMEOUT`` is the HTTP timeout in seconds. ``GROWATT_READ_ONLY=1`` hides
    every tool that changes state on Growatt's side.
    """
    env = os.environ if env is None else env

    token = env.get("GROWATT_TOKEN", "").strip()
    if not token:
        raise ConfigError(f"GROWATT_TOKEN environment variable is required. {HOW_TO_GET_ACCESS}")

    base_url = env.get("GROWATT_BASE_URL", "").strip()
    region = env.get("GROWATT_REGION", "").strip().lower()
    if base_url:
        if not base_url.startswith("https://"):
            raise ConfigError("GROWATT_BASE_URL must start with https://, the token would otherwise travel in clear.")
    else:
        if region and region not in REGIONS:
            raise ConfigError(f"Unknown GROWATT_REGION {region!r}; expected one of {', '.join(sorted(REGIONS))}.")
        base_url = REGIONS.get(region, DEFAULT_BASE_URL)

    raw_timeout = env.get("GROWATT_TIMEOUT", "").strip()
    try:
        timeout = float(raw_timeout) if raw_timeout else 30.0
    except ValueError as exc:
        raise ConfigError(f"GROWATT_TIMEOUT must be a number of seconds, got {raw_timeout!r}.") from exc
    if not math.isfinite(timeout) or timeout <= 0:
        raise ConfigError("GROWATT_TIMEOUT must be a positive, finite number of seconds.")

    read_only = env.get("GROWATT_READ_ONLY", "").strip().lower() in TRUE_VALUES

    return Settings(token=token, base_url=base_url.rstrip("/"), timeout=timeout, read_only=read_only)
