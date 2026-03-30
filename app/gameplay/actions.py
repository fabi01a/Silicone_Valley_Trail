"""Per-turn player actions: travel, rest, debug."""

from __future__ import annotations

from app.gameplay.events import trigger_random_event
from app.gameplay.stops import (
    handle_costco_stop,
    handle_final_pitch,
    handle_restaurant_stop,
    is_costco_location,
    is_restaurant_location,
)
from app.models.state import GameState
from app.services.weather import get_weather
from app.world.config import LOCATIONS, term
from app.world.distance import get_distance


def travel(state: GameState) -> None:
    """Move the team to the next location and update resources."""
    if state.progress_index >= len(LOCATIONS) - 1:
        return

    trigger_event = True
    start = state.current_location
    end = LOCATIONS[state.progress_index + 1]
    prev_location = start

    distance = get_distance(start, end)
    weather = get_weather(start, end)
    condition = weather["condition"]
    mult = float(weather["fuel_multiplier"])

    fuel_cost = int(round((distance / 2.5) * mult))

    if state.progress_index == len(LOCATIONS) - 2:
        if state.fuel < fuel_cost:
            print("⛽ Not enough fuel to make it to San Francisco.")
            print("😭 The journey ends here.")
            state.is_over = True
            state.win = False
            return

    before = {
        "fuel": state.fuel,
        "morale": state.morale,
        "bugs": state.bugs,
    }

    if condition == "rain":
        state.morale -= 2
        weather_msg = "🌧️ Rain slows the team and dampens morale 😟"
    elif condition == "heat":
        state.morale -= 4
        state.fuel -= 5
        weather_msg = "🥵 Heatwave hits. The team struggles to stay focused 😫"
    elif condition == "fog":
        state.morale -= 1
        weather_msg = "🌫️ Fog causes confusion. Progress feels slower 😕"
    else:
        weather_msg = "🌞 Clear skies. Smooth conditions for the team 😎"

    print(weather_msg)

    state.fuel -= fuel_cost
    print("🚗 You hit the road...")

    if state.fuel <= 0:
        print("\n\n⛽ You ran out of fuel. The journey ends here 😭")
        state.is_over = True
        state.win = False
        return

    changes = []
    
    if state.fuel != before["fuel"]:
        changes.append(f"⛽️ Fuel: {state.fuel - before['fuel']:+}")
    
    if state.morale != before["morale"]:
        changes.append(f"🥳 Morale: {state.morale - before['morale']:+}")
    
    if state.bugs != before["bugs"]:
        changes.append(f"👾 Bugs: {state.bugs - before['bugs']:+}")

    if changes:
        print()
        print("📊 Changes → " + " | ".join(changes))

    state.cash -= max(3, int(distance / 8))

    state.progress_index += 1
    state.sync_location()

    if condition == "heat":
        state.bugs += 1

    state.morale = max(0, state.morale - 1)

    if state.current_location == "San Mateo" and prev_location != "San Mateo":
        print("\n" + term.yellow("⏳ Final stretch ahead. Prepare wisely 😬"))

    if (
        is_costco_location(state.current_location)
        and state.current_location not in state.visited_costco
    ):
        handle_costco_stop(state)
        state.visited_costco.add(state.current_location)
        trigger_event = False

    if (
        is_restaurant_location(state.current_location)
        and state.current_location not in state.visited_restaurants
    ):
        handle_restaurant_stop(state)
        state.visited_restaurants.add(state.current_location)
        trigger_event = False

    if state.current_location == "San Francisco":
        state.day += 1
        print(
            f"\n📍 Day {state.day} — You’ve arrived in San Francisco "
            "🌉 Time for Demo Day 🤗\n"
        )
        handle_final_pitch(state)
        return

    if trigger_event:
        print()
        trigger_random_event(state, action="travel")


def rest(state: GameState) -> None:
    """Rest the team to recover morale and reduce bugs."""
    if state.cash < 12:
        print("💸 You can't afford to rest right now ☹️")
        return

    state.morale += 10
    state.fuel += 6
    state.bugs = max(0, state.bugs - 1)
    state.cash -= 12

    trigger_random_event(state, action="rest")


def debug(state: GameState) -> None:
    """Attempt to fix bugs with different possible outcomes."""
    if state.bugs == 0:
        print("🧐 The codebase is clean. Nothing to debug right now 🎺")
        return

    if state.cash < 5 or state.morale <= 5:
        print("⚠️ You can't afford to debug right now. Choose another action 🤨")
        return

    trigger_random_event(state, action="debug")
