"""Data class representing a single MITRE ATT&CK technique."""

from dataclasses import dataclass


@dataclass
class Technique:
    """A MITRE ATT&CK technique identified by a composite code and a display name."""

    code: str
    name: str
