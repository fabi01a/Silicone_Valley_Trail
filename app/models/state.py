"""Player-facing game state."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.world.config import LOCATIONS


@dataclass
class GameState:
    """
    Tracks the player's current run.

    Critical resources:
    - `cash` <= 0 => lose
    - `fuel` <= 0 => lose
    - `morale` <= 0 => lose
    """

    day: int = 1
    current_location: str = LOCATIONS[0]
    progress_index: int = 0
    visited_costco: set[str] = field(default_factory=set)
    visited_restaurants: set[str] = field(default_factory=set)

    cash: int = 100
    fuel: int = 100
    morale: int = 50
    bugs: int = 0

    is_over: bool = False
    win: bool = False

    def sync_location(self) -> None:
        """Keep `current_location` consistent with `progress_index`."""
        self.progress_index = max(0, min(self.progress_index, len(LOCATIONS) - 1))
        self.current_location = LOCATIONS[self.progress_index]
