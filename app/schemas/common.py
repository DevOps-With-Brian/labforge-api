"""Shared schema utilities."""

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    """Base Pydantic model with safe defaults."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)
