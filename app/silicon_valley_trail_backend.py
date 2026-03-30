"""
Silicon Valley Trail — CLI backend.

Logic lives under `app.world`, `app.models`, `app.services`, `app.gameplay`, and
`app.cli`. This module re-exports the public API and is the runnable entrypoint.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ is None:
    _REPO_ROOT = Path(__file__).resolve().parent.parent
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))

from app.cli.game import check_end_conditions, game_loop, prompt_action, show_player_status
from app.gameplay.actions import debug, rest, travel
from app.gameplay.events import (
    EVENTS,
    trigger_random_event,
    _event_debug_standard,
    _event_rest_mentor_call,
    _event_travel_flat_tire,
    _event_travel_roadwork,
    _event_travel_supply_drop,
)
from app.gameplay.pitch import final_pitch
from app.gameplay.stops import (
    handle_costco_stop,
    handle_final_pitch,
    handle_restaurant_stop,
    is_costco_location,
    is_restaurant_location,
)
from app.models import GameState
from app.services.weather import get_weather
from app.world.config import (
    CITY_COORDS,
    COSTCO_LOCATIONS,
    LOCATIONS,
    RESTAURANT_LOCATIONS,
    term,
)
from app.world.distance import get_distance


__all__ = [
    "CITY_COORDS",
    "COSTCO_LOCATIONS",
    "EVENTS",
    "GameState",
    "LOCATIONS",
    "RESTAURANT_LOCATIONS",
    "check_end_conditions",
    "debug",
    "final_pitch",
    "get_distance",
    "get_weather",
    "handle_costco_stop",
    "handle_final_pitch",
    "handle_restaurant_stop",
    "is_costco_location",
    "is_restaurant_location",
    "prompt_action",
    "rest",
    "show_player_status",
    "term",
    "travel",
    "trigger_random_event",
    "_event_debug_standard",
    "_event_rest_mentor_call",
    "_event_travel_flat_tire",
    "_event_travel_roadwork",
    "_event_travel_supply_drop",
    "game_loop",
]


if __name__ == "__main__":
    game_loop()
