"""Rules: actions, random events, stops, Demo Day."""

from app.gameplay.actions import debug, rest, travel
from app.gameplay.events import EVENTS, trigger_random_event
from app.gameplay.pitch import final_pitch
from app.gameplay.stops import (
    handle_costco_stop,
    handle_final_pitch,
    handle_restaurant_stop,
    is_costco_location,
    is_restaurant_location,
)

__all__ = [
    "EVENTS",
    "debug",
    "final_pitch",
    "handle_costco_stop",
    "handle_final_pitch",
    "handle_restaurant_stop",
    "is_costco_location",
    "is_restaurant_location",
    "rest",
    "travel",
    "trigger_random_event",
]
