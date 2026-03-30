"""Route distance lookups (miles)."""

from __future__ import annotations

_KNOWN_DISTANCES: dict[tuple[str, str], int] = {
    ("San Jose", "Palo Alto"): 24,
    ("Palo Alto", "Mountain View"): 12,
    ("Mountain View", "Redwood City"): 20,
    ("Redwood City", "San Francisco"): 28,
}

_DEFAULT_SEGMENT_MILES = 18


def get_distance(start: str, end: str) -> int:
    """Return driving distance between two route stops; default when unknown."""
    return _KNOWN_DISTANCES.get((start, end), _DEFAULT_SEGMENT_MILES)
