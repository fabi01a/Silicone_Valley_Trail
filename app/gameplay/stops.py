"""Special locations: Costco, restaurant, Demo Day gate."""

from __future__ import annotations

from app.gameplay.pitch import final_pitch
from app.models.state import GameState
from app.world.config import COSTCO_LOCATIONS, RESTAURANT_LOCATIONS, term


def is_costco_location(location: str) -> bool:
    return location in COSTCO_LOCATIONS


def is_restaurant_location(location: str) -> bool:
    return location in RESTAURANT_LOCATIONS


def handle_costco_stop(state: GameState) -> None:
    print(term.chartreuse("\n🛒 You spot a Costco nearby... bulk deals await 👀"))

    if state.cash < 40:
        print(term.firebrick3("💸 You can't afford a Costco run right now 😩"))
        return

    prompt = term.orange("Do you want to stop and restock? (y/n): ")
    choice = input(prompt).strip().lower()

    while choice not in {"y", "n"}:
        print(term.gold("⚠️ Please enter 'y' or 'n' ⚠️"))
        choice = input(prompt).strip().lower()

    if choice != "y":
        print("🚗 You skip Costco and stay focused on the journey 👏")
        return

    before = {
        "fuel": state.fuel,
        "cash": state.cash,
        "morale": state.morale,
    }

    state.cash -= 40
    state.fuel += 25
    state.morale += 8

    print("\n📦 You stock up in bulk. The team feels prepared 💥")

    changes = []
    if state.cash != before["cash"]:
        changes.append(f"💵 Cash: {state.cash - before['cash']:+}")
    if state.fuel != before["fuel"]:
        changes.append(f"⛽️ Fuel: {state.fuel - before['fuel']:+}")
    if state.morale != before["morale"]:
        changes.append(f"🥳 Morale: {state.morale - before['morale']:+}")

    if changes:
        print("📊 Changes → " + " | ".join(changes))


def handle_restaurant_stop(state: GameState) -> None:
    print(term.chartreuse("\n🍽️ You spot 🌭 Not Hotdog 🥤 — a team favorite 😋"))

    if state.cash < 20:
        print(term.firebrick1("💸 Not enough cash for a proper meal 😩"))
        return

    meal_prompt = term.orange("Wanna grab a team meal at 🌭 Not Hotdog 🥤? (y/n): ")
    choice = input(meal_prompt).strip().lower()

    while choice not in {"y", "n"}:
        print(term.gold("⚠️ Please enter 'y' or 'n' ⚠️"))
        choice = input(meal_prompt).strip().lower()

    if choice != "y":
        print("✋ You skip the meal and keep moving 🏃💨")
        return

    before = {
        "cash": state.cash,
        "morale": state.morale,
        "bugs": state.bugs,
    }

    state.cash -= 20
    state.morale += 12
    if state.bugs > 0:
        state.bugs -= 1

    print("\n🐷 The team feels recharged after a good meal. Spirits are high 😊")

    changes = []
    if state.cash != before["cash"]:
        changes.append(f"💵 Cash: {state.cash - before['cash']:+}")
    if state.morale != before["morale"]:
        changes.append(f"🥳 Morale: {state.morale - before['morale']:+}")
    if state.bugs != before["bugs"]:
        changes.append(f"👾 Bugs: {state.bugs - before['bugs']:+}")

    if changes:
        print("📊 Changes → " + " | ".join(changes))


def handle_final_pitch(state: GameState) -> None:
    print(term.green3("\n🎤 You’ve made it to Demo Day 🙌\n"))

    failed = False

    if state.morale < 40:
        print(term.firebrick1("😬 Morale is too low. The team can't present 😖"))
        failed = True

    if state.bugs >= 5:
        print(term.firebrick1("💥 Too many bugs. The demo crashes in front of investors 😖"))
        failed = True
    
    if failed:
        print()
        state.is_over = True
        state.win = False
        return

    prompt = term.orange("Are you ready to present? (y/n): ")
    choice = input(prompt).strip().lower()

    while choice not in {"y", "n"}:
        print(term.gold("⚠️ Please enter 'y' or 'n' ⚠️"))
        choice = input(prompt).strip().lower()

    if choice != "y":
        print(term.firebrick1("🫥 You hesitate and the opportunity passes you by... 🎺"))
        state.is_over = True
        state.win = False
        return

    state.is_over = True
    state.win = final_pitch(state)
