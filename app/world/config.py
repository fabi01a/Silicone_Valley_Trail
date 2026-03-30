"""Static game configuration: route, coordinates, terminal handle."""

from __future__ import annotations

from blessed import Terminal

term = Terminal()

LOCATIONS = [
    "San Jose",
    "Santa Clara",
    "Palo Alto",
    "Redwood City",
    "San Carlos",
    "Mountain View",
    "San Mateo",
    "Daly City",
    "San Francisco",
]

CITY_COORDS = {
    "San Jose": (37.3382, -121.8863),
    "Santa Clara": (37.3541, -121.9552),
    "Palo Alto": (37.4419, -122.1430),
    "Redwood City": (37.4852, -122.2364),
    "San Carlos": (37.5072, -122.2605),
    "Mountain View": (37.3861, -122.0839),
    "San Mateo": (37.5630, -122.3255),
    "Daly City": (37.6879, -122.4702),
    "San Francisco": (37.7749, -122.4194),
}

COSTCO_LOCATIONS = frozenset({"Santa Clara", "Daly City"})

RESTAURANT_LOCATIONS = frozenset({"Palo Alto", "Mountain View"})
