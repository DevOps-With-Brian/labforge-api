"""Compatibility layer for schema imports.

Prefer importing from ``app.schemas`` directly. This module re-exports the
health response schema for older imports.
"""

from app.schemas.health import HealthResponse

__all__ = ["HealthResponse"]
