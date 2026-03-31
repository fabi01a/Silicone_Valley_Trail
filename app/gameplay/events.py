"""Weighted random events triggered after travel, rest, or debug."""

from __future__ import annotations

import random
from typing import Callable, Dict, List

from app.models.state import GameState
from app.world.config import term

EventEffect = Callable[[GameState], str]


def _event_debug_breakthrough(state: GameState) -> str:
    state.bugs = max(0, state.bugs - 4)
    state.morale += 3
    return "💡 Breakthrough! A tricky bug gets resolved cleanly 🛜"


def _event_debug_standard(state: GameState) -> str:
    state.bugs = max(0, state.bugs - 3)
    state.morale -= 5
    state.cash -= 5
    return "☄️ Gilfoyle cleans up the codebase. Bugs decrease, but morale takes a hit 📉"


def _event_rest_mentor_call(state: GameState) -> str:
    state.morale += 8
    state.bugs = max(0, state.bugs - 2)
    state.cash -= 10
    return "🤖 A mentor schedules time with your crew. Bugs drop, morale rises 🎂"


def _event_rest_beta_users(state: GameState) -> str:
    state.morale += 2
    state.bugs += 2
    return "🗣️ Beta users give feedback. Morale spikes, but new bugs appear 🤨"


def _event_travel_roadwork(state: GameState) -> str:
    state.fuel -= 15
    state.morale -= 1
    state.bugs += 2
    return "🚧 Roadwork slowed you down. Fuel and morale take a hit ⬇️"


def _event_travel_flat_tire(state: GameState) -> str:
    state.fuel -= 10
    state.cash -= 10
    state.morale -= 2
    return "🛞 Flat tire! Gilfoyle fixes it, but it costs time and money 💸"


def _event_travel_hackathon(state: GameState) -> str:
    if random.random() < 0.6:
        state.cash += 30
        state.morale += 4
        state.bugs += 3
        return "⭐️ Hackathon win! You secure some funding, but introduce new bugs 🥲"
    state.morale -= 5
    state.cash -= 10
    return term.orange("😓 Hackathon flop. Time wasted and morale drops 😩")


def _event_travel_supply_drop(state: GameState) -> str:
    state.cash += 15
    state.fuel += 20
    state.morale += 5
    state.bugs = max(0, state.bugs - 1)
    return term.chartreuse("✈️ A passing Pied Piper Plane drops supplies! The team catches a lucky break 🎁")


EVENTS: List[Dict[str, object]] = [
    {
        "name": "Roadwork Delay",
        "applies_to": {"travel"},
        "effect": _event_travel_roadwork,
        "weight": 3,
    },
    {
        "name": "Flat Tire",
        "applies_to": {"travel"},
        "effect": _event_travel_flat_tire,
        "weight": 2,
    },
    {
        "name": "Hackathon",
        "applies_to": {"travel"},
        "effect": _event_travel_hackathon,
        "optional": True,
        "weight": 2,
    },
    {
        "name": "Supply Drop",
        "applies_to": {"travel"},
        "effect": _event_travel_supply_drop,
        "optional": True,
        "weight": 1,
    },
    {
        "name": "Standard Debug",
        "applies_to": {"debug"},
        "effect": _event_debug_standard,
        "weight": 3,
    },
    {
        "name": "Breakthrough",
        "applies_to": {"debug"},
        "effect": _event_debug_breakthrough,
        "weight": 1,
    },
    {
        "name": "Mentor Call",
        "applies_to": {"rest"},
        "effect": _event_rest_mentor_call,
        "weight": 2,
    },
    {
        "name": "Beta Users",
        "applies_to": {"rest"},
        "effect": _event_rest_beta_users,
        "weight": 2,
    },
]


def trigger_random_event(state: GameState, action: str) -> None:
    """Pick and apply a random event for `action`; optional events prompt the player."""
    eligible = [e for e in EVENTS if action in e["applies_to"]]

    if not eligible:
        return

    weights = [e.get("weight", 1) for e in eligible]
    event = random.choices(eligible, weights=weights, k=1)[0]

    if event.get("optional", False):
        print(term.deepskyblue1(f"\n⚡Opportunity: {event['name']} ⚡"))
        prompt = "Do you want to take this opportunity? (y/n): "
        choice = input(term.orange(prompt)).strip().lower()

        while choice not in {"y", "n"}:
            print(term.gold("⚠️ Please enter 'y' or 'n' ⚠️"))
            choice = input(term.orange(prompt)).strip().lower()

        if choice != "y":
            print("😶 You passed on the opportunity. The day continues smoothly 😀")
            return

    effect: EventEffect = event["effect"]

    before = {
        "fuel": state.fuel,
        "cash": state.cash,
        "morale": state.morale,
        "bugs": state.bugs,
    }

    print()
    print(effect(state))

    delta_fuel = state.fuel - before["fuel"]
    delta_cash = state.cash - before["cash"]
    delta_morale = state.morale - before["morale"]
    delta_bugs = state.bugs - before["bugs"]

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
