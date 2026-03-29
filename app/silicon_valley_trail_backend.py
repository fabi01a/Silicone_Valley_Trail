"""
Silicon Valley Trail (CLI backend)

This file is intentionally self-contained for now:
- Keep everything readable and simple.
- Avoid frameworks / async / databases.
- Structure code so it could later be split into modules.
"""

from __future__ import annotations

import random
from blessed import Terminal
from dataclasses import dataclass, field
from typing import Callable, Dict, List

term = Terminal()

# --- 1) Map / Locations ---
# Each turn (day), the player can move forward along this route.
LOCATIONS = [
    "San Jose",
    "Santa Clara",
    "Palo Alto",
    "Redwood City",
    "Mountain View",
    "San Mateo",
    "Daly City",
    "San Francisco",
]

COSTCO_LOCATIONS = {
    "Santa Clara",
    "San Mateo",
    "Daly City",
}

def _last_location() -> str:
    return LOCATIONS[-1]

def is_costco_location(location:str) -> bool:
    return location in COSTCO_LOCATIONS

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
    visited_costco: set[str] = field(default_factory=set)

    cash: int = 100
    fuel: int = 100
    morale: int = 50

    # Optional "startup-y" stats (requested).
    bugs: int = 0

    # Game end flags.
    is_over: bool = False
    win: bool = False

    def sync_location(self) -> None:
        """Keep `current_location` consistent with `progress_index`."""
        self.progress_index = max(0, min(self.progress_index, len(LOCATIONS) - 1))
        self.current_location = LOCATIONS[self.progress_index]

def handle_costco_stop(state: GameState) -> None:
    print(term.chartreuse("\n🛒 You spot a Costco nearby... bulk deals await 👀"))

    # Guard: not enough cash
    if state.cash < 40:
        print(term.firebrick3("💸 You can't afford a Costco run right now 😩"))
        return

    choice = input("Do you want to stop and restock? (y/n): ").strip().lower()
    print()

    while choice not in {"y", "n"}:
        print("⚠️ Please enter 'y' or 'n'.")
        choice = input("Do you want to take this opportunity? (y/n): ").strip().lower()
    
    if choice not in {"y", "n"}:
        print("⚠️ Please enter 'y' or 'n'.")
        return

    if choice != "y":
        print("🚗 You skip Costco and stay focused on the journey 👏")
        return

    # Apply tradeoff
    before = {
        "fuel": state.fuel,
        "cash": state.cash,
        "morale": state.morale,
        "bugs": state.bugs,
    }

    state.cash -= 40
    state.fuel += 25
    state.morale += 8
    state.bugs = max(0, state.bugs - 2)

    print("\n📦 You stock up in bulk. The team feels prepared 💥")

    # Show deltas (consistent with your event system)
    changes = []
    if state.fuel != before["fuel"]:
        changes.append(f"⛽️ Fuel: {state.fuel - before['fuel']:+}")
    if state.cash != before["cash"]:
        changes.append(f"💵 Cash: {state.cash - before['cash']:+}")
    if state.morale != before["morale"]:
        changes.append(f"🥳 Morale: {state.morale - before['morale']:+}")
    if state.bugs != before["bugs"]:
        changes.append(f"👾 Bugs: {state.bugs - before['bugs']:+}")

    if changes:
        print("📊 Changes → " + " | ".join(changes))


def handle_final_pitch(state: GameState) -> None:
    print("\n🎤 You’ve made it to Demo Day 🙌\n")

    # ❌ Morale too low
    if state.morale < 40:
        print("😬 Your team isn't ready to present. Morale is too low 😖")
        state.is_over = True
        state.win = False
        return

    # ❌ TOO MANY BUGS → block presentation
    if state.bugs >= 8:
        print("💥 Your product is too unstable to demo. There are too many bugs 🕸️")
        print("📢 You should have debugged more before arriving 😖")
        state.is_over = True
        state.win = False
        return

    choice = input("Are you ready to present? (y/n): ").strip().lower()

    while choice not in {"y", "n"}:
        print("⚠️ Please enter 'y' or 'n'.")

    choice = input("Do you want to take this opportunity? (y/n): ").strip().lower()
    if choice != "y":
        print("🧠 You hesitate too long... the opportunity passes you by 🎺")
        state.is_over = True
        state.win = False
        return

    state.is_over = True
    state.win = final_pitch(state)


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

def _event_debug_breakthrough(state: GameState) -> str:
    state.bugs = max(0, state.bugs - 4)
    state.morale += 3
    return "💡 Breakthrough! A tricky bug gets resolved cleanly 🛜" 

def _event_debug_nothing(state: GameState) -> str:
    return "😐 You stare at the code... nothing stands out."

def _event_debug_standard(state: GameState) -> str:
    state.bugs = max(0, state.bugs - 3)
    state.morale -= 5
    state.cash -= 5
    return "🔄 Gilfoyle cleans up the codebase. Bugs decrease, but morale takes a hit 📉"

def _event_rest_mentor_call(state: GameState) -> str:
    state.morale += 8
    state.bugs = max(0, state.bugs - 2)
    state.cash -= 10  # paying for someone’s time / perks
    return "🤖 A mentor schedules time with your crew. Bugs drop; morale rises ↪️"

def _event_rest_beta_users(state: GameState) -> str:
    state.morale += 2
    state.bugs += 2  # feedback introduces new issues
    return "🗣️ Beta users give feedback. Morale spikes, but new bugs appear 🤨"

def _event_travel_roadwork(state: GameState) -> str:
    state.fuel -= 15
    state.morale -= 1
    state.bugs += 1
    return "🚧 Roadwork slowed you down. Fuel and morale take a hit ⬇️"

def _event_travel_flat_tire(state: GameState) -> str:
    state.fuel -= 10
    state.cash -= 10
    state.morale -= 2
    return "🛞 Flat tire! Gilfoyle fixes it, but it costs time and money 💸"

def _event_travel_hackathon(state: GameState) -> str:
    if random.random() < 0.6:
        state.cash += 30   # ⬅️ increase from 25
        state.morale += 4
        state.bugs += 2
        return "💻 Hackathon win! You secure funding, but introduce new bugs 🥲"
    else:
        state.morale -= 5
        state.cash -= 10
        return "😓 Hackathon flop. Time wasted and morale drops 😩"

def _event_travel_supply_drop(state: GameState) -> str:
    state.cash += 15
    state.fuel += 20
    state.morale += 5
    state.bugs = max(0, state.bugs - 1)

    return "✈️ A passing plane drops supplies! The team catches a lucky break 🎁"

def _event_travel_nothing(state: GameState) -> str:
    return "🙂 Nothing unusual happens today 🙃"


EVENTS: List[Dict[str, object]] = [
    #Travel events
    {"name": "Roadwork Delay", "applies_to": {"travel"}, "effect": _event_travel_roadwork, "weight": 3},
    {"name": "Flat Tire", "applies_to": {"travel"}, "effect": _event_travel_flat_tire, "weight": 2},
    {"name": "Nothing Happens", "applies_to": {"travel"}, "effect": _event_travel_nothing, "weight": 1},
    {"name": "Hackathon", "applies_to": {"travel"}, "effect": _event_travel_hackathon, "optional": True, "weight": 2},
    {"name": "Supply Drop", "applies_to": {"travel"}, "effect": _event_travel_supply_drop, "optional": True, "weight": 1},  
    
    {"name": "Breakthrough", "applies_to": {"debug"}, "effect": _event_debug_breakthrough, "weight": 2},
    {"name": "Standard Debug", "applies_to": {"debug"}, "effect": _event_debug_standard, "weight": 3},
    {"name": "Breakthrough", "applies_to": {"debug"}, "effect": _event_debug_breakthrough, "weight": 1},    

    #Rest events
    {"name": "Mentor Call", "applies_to": {"rest"}, "effect": _event_rest_mentor_call, "weight": 2},
    {"name": "Beta Users", "applies_to": {"rest"}, "effect": _event_rest_beta_users, "weight": 2},

]


def trigger_random_event(state: GameState, action: str) -> str:
    """
    Randomly selects an event from a list.
    Optional events can be accepted or skipped by the player.
    Also prints resource changes for clarity.
    """
    eligible = [e for e in EVENTS if action in e["applies_to"]]

    if not eligible:
        print("😐 Nothing unusual happens today 🙃")
        return ""

    # Weighted selection
    weights = [e.get("weight", 1) for e in eligible]
    event = random.choices(eligible, weights=weights, k=1)[0]

    # Handle optional events
    if event.get("optional", False):
        print(term.chartreuse(f"\n⚡Opportunity: {event['name']} ⚡"))
        choice = input("Do you want to take this opportunity? (y/n): ").strip().lower()

        while choice not in {"y", "n"}:
            print("⚠️ Please enter 'y' or 'n'.")
            choice = input("Do you want to take this opportunity? (y/n): ").strip().lower()

        if choice != "y":
            print("🙂‍↔️ You passed on the opportunity. The day continues smoothly 😀")
            return ""

    # Capture state BEFORE event
    before = {
        "fuel": state.fuel,
        "cash": state.cash,
        "morale": state.morale,
        "bugs": state.bugs,
    }

    # Apply event
    effect: EventEffect = event["effect"]  # type: ignore[assignment]
    message = effect(state)

    # Print event message
    print("\n" + message)

    # Compute deltas
    delta_fuel = state.fuel - before["fuel"]
    delta_cash = state.cash - before["cash"]
    delta_morale = state.morale - before["morale"]
    delta_bugs = state.bugs - before["bugs"]

    # Only show changes if something changed
    changes = []

    if delta_fuel != 0:
        changes.append(f"⛽️ Fuel: {delta_fuel:+}")
    if delta_cash != 0:
        changes.append(f"💵 Cash: {delta_cash:+}")
    if delta_morale != 0:
        changes.append(f"🥳 Morale: {delta_morale:+}")
    if delta_bugs != 0:
        changes.append(f"👾 Bugs: {delta_bugs:+}")

    if changes:
        print("📊 Changes → " + " | ".join(changes))

    return ""

    
def check_end_conditions(state: GameState) -> None:
    """Set game over state and determine win/loss."""

    # Lose conditions
    if state.cash <= 0:
        print()
        print("💸 You ran out of cash. The startup collapses 😭")
        state.is_over = True
        state.win = False
        return
    
    if state.cash < 12:
        print("💸 You can't afford to rest right now ☹️")
        return

    if state.fuel <= 0:
        print("⛽ You ran out of fuel. You can't continue the journey 😭")
        state.is_over = True
        state.win = False
        return

    if state.morale <= 0:
        print("😠 The team loses all morale and quits 🚨 ")
        state.is_over = True
        state.win = False
        return

    # Reached San Francisco → final pitch
    if state.progress_index >= len(LOCATIONS) - 1:
        return


# --- 6) Action functions ---
def travel(state: GameState) -> None:
    """Move the team to the next location and update resources."""

    # Already at destination
    if state.progress_index >= len(LOCATIONS) - 1:
        return

    # --- Determine next leg ---
    start = state.current_location
    end = LOCATIONS[state.progress_index + 1]

    distance = get_distance(start, end)
    weather = get_weather(start, end)

    fuel_needed = int(round((distance / 2.5) * float(weather["fuel_multiplier"])))
    condition = weather["condition"]

    # --- Final leg check (Daly City → SF) ---
    if state.progress_index == len(LOCATIONS) - 2:
        if state.fuel < fuel_needed:
            print("⛽ Not enough fuel to make it to San Francisco.")

            # --- simulate max possible recovery ---
            max_possible_fuel = state.fuel

            # if they can afford Costco
            if state.cash >= 40:
                max_possible_fuel += 25

            # else if they can afford rest
            elif state.cash >= 12:
                max_possible_fuel += 10  # whatever your rest gives

            # 🚨 If STILL not enough → game over
            if max_possible_fuel < fuel_needed:
                print("💸 Even with recovery, you can't make it to San Francisco.")
                print("🚗💨 You're stranded just before the finish line.")
                state.is_over = True
                state.win = False
                return

            print("🚨 You need to refuel before continuing 😵‍💫")
            return

    # --- Weather effects ---
    if condition == "rain":
        state.bugs += 2
        state.morale -= 2
        print("🌧️ Rain slows the team. Bugs increase and morale dips 😟")

    elif condition == "heat":
        state.bugs += 3
        state.morale -= 4
        state.fuel -= 10
        print("🥵 Heatwave hits. The team struggles and bugs pile up 😫")

    elif condition == "fog":
        state.bugs += 1
        state.morale -= 1
        print("🌫️ Fog causes confusion. Minor bugs introduced 😕")

    else:
        print("🌞 Clear skies. Smooth conditions for the team 😎")

    # --- Fuel cost ---
    fuel_cost = int(round((distance / 2.5) * float(weather["fuel_multiplier"])))
    state.fuel -= fuel_cost
    print(f"🚗 Fuel cost: {fuel_cost} | ⛽️ Fuel remaining: {state.fuel}")

    # 🚨 Immediate fail if fuel drops to 0 or below
    if state.fuel <= 0:
        print("⛽ You ran out of fuel. The journey ends here.")
        state.is_over = True
        state.win = False
        return

    # --- Travel cost ---
    state.cash -= max(3, int(distance / 8))

    # --- Move forward ---
    state.progress_index += 1
    state.sync_location()

    # --- Final stretch message (UI only) ---
    if state.progress_index == len(LOCATIONS) - 3:
        print(term.yellow("\n⏳ Final stretch ahead. Prepare wisely.\n"))

    # --- Costco opportunity ---
    if (
        is_costco_location(state.current_location)
        and state.current_location not in state.visited_costco
    ):
        handle_costco_stop(state)
        state.visited_costco.add(state.current_location)

    # --- Arrival at SF ---
    if state.current_location == "San Francisco":
        state.day += 1
        print(f"\n📍 Day {state.day} — You’ve arrived in San Francisco. Time for Demo Day 🤞🏾\n")
        handle_final_pitch(state)
        return

    # --- Trigger random event ---
    print()
    trigger_random_event(state, action="travel")


def rest(state: GameState) -> None:
    """Rest the team to recover morale and reduce bugs."""
    # Rest helps morale, slightly refuels, and helps with bugs.
    state.morale += 10
    state.fuel += 6
    state.bugs = max(0, state.bugs - 1)

    # Resting is not free.
    state.cash -= 12

    message = trigger_random_event(state, action="rest")
    print(message)


def debug(state: GameState) -> None:
    """Attempt to fix bugs with different possible outcomes."""

    if state.bugs == 0:
        print("🧐 The codebase is clean. Nothing to debug right now 🎺")
        return

    if state.cash < 5 or state.morale <= 5:
        print("⚠️ You can't afford to debug right now. Choose another action.")
        return

    trigger_random_event(state, action="debug")


def final_pitch(state: GameState) -> bool:
    """
    Final pitch at San Francisco.
    Determines win or loss.
    """
    print("\n🎤 Final Demo Day Pitch —  Dinesh is presenting...🙏\n")

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



    if random.random() < success_chance:
        print("🚀 The demo is flawless. Investors are impressed 💰")
        return True
    else:
        print("💥 The demo crashes. The room goes silent ⬇️")
        return False


# --- 7) Game loop ---
def show_player_status(state: GameState) -> None:
    """Print the current state to the CLI."""
    print()
    print(term.green3("\n===== Silicon Valley Trail ====="))
    print(f"Day: {state.day}")
    print(f"{term.green3('Location:')} {term.green3(state.current_location)}")
    print(f"💵 Cash: {state.cash} | ⛽️ Fuel: {state.fuel} | 🥳 Morale: {state.morale} | 👾 Bugs: {state.bugs}")


def prompt_action() -> str:
    """Ask the player what to do this day."""
    print(term.green3("\nChoose an action:"))
    print("1) 🚗 travel  - move to the next location")
    print("2) 🥱 rest    - recover morale and refuel a bit")
    print("3) ⌨️  debug   - fix bugs but costs morale")
    print()
    choice = input(term.green3("> ")).strip().lower()
    print()

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
    print(term.green3("\n=== Game Over ==="))
    if state.win:
        print(term.yellow("🙌 You reached San Francisco and killed the presentation!!! The future is yours 🔮"))
    else:
        print(" 🚗💨 Your run ended. One more iteration and you'll make it 🍀")


if __name__ == "__main__":
    game_loop()

