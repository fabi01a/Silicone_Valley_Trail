"""
Silicon Valley Trail (CLI backend)

This file is intentionally self-contained for now:
- Keep everything readable and simple.
- Avoid frameworks / async / databases.
- Structure code so it could later be split into modules.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Dict, List


# --- 1) Map / Locations ---
# Each turn (day), the player can move forward along this route.
LOCATIONS: List[str] = [
    "San Jose",
    "Palo Alto",
    "Mountain View",
    "Redwood City",
    "San Francisco",
]


def _last_location() -> str:
    return LOCATIONS[-1]


# --- 2) Game State ---
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

    cash: int = 100
    fuel: int = 100
    morale: int = 50

    # Optional "startup-y" stats (requested).
    hype: int = 0
    bugs: int = 0

    # Game end flags.
    is_over: bool = False
    win: bool = False

    def sync_location(self) -> None:
        """Keep `current_location` consistent with `progress_index`."""
        self.progress_index = max(0, min(self.progress_index, len(LOCATIONS) - 1))
        self.current_location = LOCATIONS[self.progress_index]


# --- 3) "API" placeholders (mock data for now) ---
def get_weather(start: str, end: str) -> Dict[str, str | float]:
    """
    Mock weather provider.
    Returns a simple object that affects travel costs/morale.
    """
    # Deterministic-ish choice based on route text, so runs feel stable.
    seed = sum(ord(c) for c in (start + "->" + end))
    rng = random.Random(seed)
    roll = rng.random()

    if roll < 0.2:
        return {"condition": "fog", "fuel_multiplier": 1.15, "morale_delta": -3}
    elif roll < 0.4:
        return {"condition": "rain", "fuel_multiplier": 1.25, "morale_delta": -6}
    elif roll < 0.6:
        return {"condition": "heat", "fuel_multiplier": 1.2, "morale_delta": -5}
    elif roll < 0.75:
        return {"condition": "wind", "fuel_multiplier": 1.1, "morale_delta": -2}
    else:
        return {"condition": "clear", "fuel_multiplier": 1.0, "morale_delta": 1}


def get_distance(start: str, end: str) -> int:
    """
    Mock distance provider (miles).
    Travel consumes fuel based on route distance.
    """
    distances = {
        ("San Jose", "Palo Alto"): 24,
        ("Palo Alto", "Mountain View"): 12,
        ("Mountain View", "Redwood City"): 20,
        ("Redwood City", "San Francisco"): 28,
    }
    return distances.get((start, end), 18)


# --- 4) Event system ---
# Each event is represented as a dict with:
# - name: user-facing string
# - applies_to: which actions can trigger it
# - effect: function that mutates GameState

EventEffect = Callable[[GameState], str]


def _event_travel_roadwork(state: GameState) -> str:
    state.fuel -= 15
    state.morale -= 1
    state.bugs += 1
    state.hype = max(0, state.hype - 2)
    return "🚧 Roadwork slowed you down. Fuel and morale take a hit ⬇️"

def _event_rest_mentor_call(state: GameState) -> str:
    state.morale += 8
    state.hype += 2
    state.bugs = max(0, state.bugs - 2)
    state.cash -= 10  # paying for someone’s time / perks
    return "🧙🏻‍♀️ A mentor schedules time with your crew. Bugs drop; morale rises 💪🏼"

def _event_rest_beta_users(state: GameState) -> str:
    state.morale += 2
    state.hype += 5
    state.bugs += 2  # feedback introduces new issues
    return "🗣️ Beta users give feedback. Hype spikes, but new bugs appear 👾"

def _event_travel_flat_tire(state: GameState) -> str:
    state.fuel -= 10
    state.cash -= 10
    state.morale -= 2
    return "🛞 Flat tire! Gilfoyle fixes it, but it costs time and money 💸"

def _event_travel_hackathon(state: GameState) -> str:
    if random.random() < 0.6:
        state.cash += 25
        state.hype += 5
        state.morale += 3
        state.bugs += 2
        return "💻 Hackathon win! Big gains, but new bugs introduced 👾"
    else:
        state.morale -= 4
        state.cash -= 10
        return "😓 Hackathon flop. Time wasted and morale drops 😩"

def _event_travel_supply_run(state: GameState) -> str:
    state.cash -= 25
    state.fuel += 15
    state.morale += 2
    return "🛒 Quick Costco stop. Supplies restocked, but it costs cash 💸"

def _event_travel_nothing(state: GameState) -> str:
    return "😐 Nothing unusual happens today 🙃"


EVENTS: List[Dict[str, object]] = [
    #Travel events
    {"name": "Roadwork Delay", "applies_to": {"travel"}, "effect": _event_travel_roadwork, "weight": 3},
    {"name": "Flat Tire", "applies_to": {"travel"}, "effect": _event_travel_flat_tire, "weight": 2},
    {"name": "Nothing Happens", "applies_to": {"travel"}, "effect": _event_travel_nothing, "weight": 3},
    {"name": "Hackathon", "applies_to": {"travel"}, "effect": _event_travel_hackathon, "optional": True, "weight": 1},
    {"name": "Supply Run", "applies_to": {"travel"}, "effect": _event_travel_supply_run, "optional": True, "weight": 1},  
    
    #Rest events
    {"name": "Mentor Call", "applies_to": {"rest"}, "effect": _event_rest_mentor_call, "weight": 2},
    {"name": "Beta Users", "applies_to": {"rest"}, "effect": _event_rest_beta_users, "weight": 2},
    {"name": "Nothing Happens", "applies_to": {"travel"}, "effect": _event_travel_nothing, "weight": 1},

]


def trigger_random_event(state: GameState, action: str) -> str:
    """
    Randomly selects an event from a list.
    Optional events can be accepted or skipped by the player.
    """
    eligible = [e for e in EVENTS if action in e["applies_to"]]
    if not eligible:
        return "No event this time."

    event = random.choice(eligible)

    # Check if event is optional
    is_optional = event.get("optional", False)

    if is_optional:
        print(f"\n⚡ Opportunity: {event['name']}")
        choice = input("Do you want to take this opportunity? (y/n): ").strip().lower()

        if choice != "y":
            return "🙂‍↔️ You passed on the opportunity. The day continues smoothly 😀"

    # Apply event effect
    effect: EventEffect = event["effect"]  # type: ignore[assignment]
    return effect(state)
    
# --- 5) Win/Lose conditions ---
def check_end_conditions(state: GameState) -> None:
    """Set game over state and determine win/loss."""

    # Lose conditions first
    if state.cash <= 0 or state.fuel <= 0 or state.morale <= 0:
        state.is_over = True
        state.win = False
        return

    # Reached San Francisco → trigger final pitch
    if state.progress_index >= len(LOCATIONS) - 1:
        state.is_over = True
        state.win = final_pitch(state)


# --- 6) Action functions ---
def travel(state: GameState) -> None:
    """Move the team to the next location and update resources."""
    if state.progress_index >= len(LOCATIONS) - 1:
        # Already at destination.
        return

    start = state.current_location
    end = LOCATIONS[state.progress_index + 1]

    distance = get_distance(start, end)
    weather = get_weather(start, end)
    condition = weather["condition"]

    if condition == "rain":
        state.bugs += 2
        state.morale -= 2
        print("🌧️ Rain slows the team. Bugs increase and morale dips 😟")

    elif condition == "heat":
        state.bugs += 3
        state.morale -= 3
        print("🥵 Heatwave hits. The team struggles and bugs pile up 😫")

    elif condition == "fog":
        state.bugs += 1
        state.morale -= 1
        print("🌫️ Fog causes confusion. Minor bugs introduced 😕")
    
    else:
        print("🌞 Clear skies. Smooth conditions for the team 😎")
   
    # Core travel costs:
    # - Fuel cost scales with distance.
    # - Morale can drop if weather is bad.
    fuel_cost = int(round((distance / 4) * float(weather["fuel_multiplier"])))
    state.fuel -= fuel_cost
    state.morale += int(weather["morale_delta"])

    # Travel also costs money (food, commuting, logistics).
    state.cash -= max(3, int(distance / 8))

    # Move forward one step along the map.
    state.progress_index += 1
    state.sync_location()

    # One random event for travel days.
    message = trigger_random_event(state, action="travel")
    print(message)


def rest(state: GameState) -> None:
    """Rest the team to recover morale and reduce bugs."""
    # Rest helps morale, slightly refuels, and helps with bugs.
    state.morale += 10
    state.fuel += 10
    state.bugs = max(0, state.bugs - 1)

    # Resting is not free.
    state.cash -= 12

    message = trigger_random_event(state, action="rest")
    print(message)


def debug(state: GameState) -> None:
    """Reduce bugs at the cost of morale and some cash."""
    state.bugs = max(0, state.bugs - 3)
    state.morale -= 5
    state.cash -= 5

    print(" 🙆🏻‍♂️ Gilfoyle cleans up the codebase. Bugs decrease, but morale takes a hit 📉")

    message = trigger_random_event(state, action="debug")
    print(message)


def final_pitch(state: GameState) -> bool:
    """
    Final pitch at San Francisco.
    Determines win or loss.
    """
    print("\n🎤 Final Demo Day Pitch — 🙎🏾‍♂️ Dinesh is presenting...\n")

    success_chance = 0.4

    # morale impact
    if state.morale > 65:
        success_chance += 0.2
    elif state.morale < 40:
        success_chance -= 0.2

    # bugs impact HARD FAIL
    if state.bugs >= 8:
        print("💥 Too many bugs. The demo crashes instantly ⬇️")
        return False

    # bugs impact SOFT PENALTY
    if state.bugs > 5:
        success_chance -= 0.3


    # hype (small bonus)
    if state.hype > 5:
        success_chance += 0.1

    success_chance = max(0.1, min(0.85, success_chance))

    if random.random() < success_chance:
        print("🚀 The demo is flawless. Investors are impressed 💰")
        return True
    else:
        print("💥 The demo crashes. The room goes silent ⬇️")
        return False


# --- 7) Game loop ---
def show_player_status(state: GameState) -> None:
    """Print the current state to the CLI."""
    print("\n=== Silicon Valley Trail ===")
    print(f"Day: {state.day}")
    print(f"Location: {state.current_location}")
    print(f"Cash: {state.cash} | Fuel: {state.fuel} | Morale: {state.morale}")
    print(f"Hype: {state.hype} | Bugs: {state.bugs}")


def prompt_action() -> str:
    """Ask the player what to do this day."""
    print("\nChoose an action:")
    print("1) travel  - move to the next location")
    print("2) rest    - recover morale and refuel a bit")
    print("3) debug   - fix bugs but costs morale")
    choice = input("> ").strip().lower()

    if choice in {"1", "travel", "t"}:
        return "travel"
    if choice in {"2", "rest", "r"}:
        return "rest"
    if choice in {"3", "debug", "d"}:
        return "debug"
    return ""


def game_loop(start_cash: int = 100, start_fuel: int = 100, start_morale: int = 50) -> None:
    """
    Basic CLI loop:
    - shows player status
    - prompts for an action
    - updates state
    - increments the day
    - checks win/lose conditions
    """
    state = GameState(cash=start_cash, fuel=start_fuel, morale=start_morale)

    while not state.is_over:
        show_player_status(state)

        action = ""
        while not action:
            action = prompt_action()
            if not action:
                print("Invalid choice. Enter `travel`, `rest`, or `debug`.")

        # Apply action effects.
        if action == "travel":
            travel(state)
        elif action == "rest":
            rest(state)
        elif action == "debug":
            debug(state)

        # Day increments after action resolves.
        state.day += 1

        # Keep end-of-loop stats clean.
        state.sync_location()

        # Check win/lose.
        check_end_conditions(state)

    # Final result.
    print("\n=== Game Over ===")
    if state.win:
        print("🙌🏼 You reached San Francisco. The future is yours 🔮")
    else:
        print(" 🚗💨 Your run ended. One more iteration and you'll make it 🤞🏾")


if __name__ == "__main__":
    game_loop()

