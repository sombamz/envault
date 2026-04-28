"""Profile management utilities for envault."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

PROFILE_NAME_RE = re.compile(r'^[a-zA-Z0-9_\-\.]{1,64}$')


@dataclass
class Profile:
    """Represents a named collection of environment variables."""

    name: str
    variables: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None

    def __post_init__(self) -> None:
        validate_profile_name(self.name)

    def set(self, key: str, value: str) -> None:
        """Add or update a variable."""
        if not key:
            raise ValueError("Variable key must not be empty.")
        self.variables[key] = value

    def unset(self, key: str) -> None:
        """Remove a variable; raises KeyError if not present."""
        if key not in self.variables:
            raise KeyError(f"Key '{key}' not found in profile '{self.name}'.")
        del self.variables[key]

    def keys(self) -> List[str]:
        """Return sorted list of variable keys."""
        return sorted(self.variables.keys())

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Return the value for *key*, or *default* if the key is not present."""
        return self.variables.get(key, default)

    def to_dict(self) -> Dict:
        """Serialise to a plain dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "variables": dict(self.variables),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Profile":
        """Deserialise from a plain dictionary."""
        return cls(
            name=data["name"],
            variables=data.get("variables", {}),
            description=data.get("description"),
        )


def validate_profile_name(name: str) -> None:
    """Raise ValueError if *name* is not a valid profile identifier."""
    if not PROFILE_NAME_RE.match(name):
        raise ValueError(
            f"Invalid profile name '{name}'. "
            "Only letters, digits, hyphens, underscores, and dots are allowed "
            "(1-64 characters)."
        )


def merge_profiles(base: Profile, override: Profile) -> Profile:
    """Return a new Profile with *override* variables layered on top of *base*."""
    merged_vars = {**base.variables, **override.variables}
    return Profile(
        name=base.name,
        variables=merged_vars,
        description=base.description,
    )
