"""Demo Day outcome resolution."""

from __future__ import annotations

import random

from app.models.state import GameState
from app.world.config import term


def final_pitch(state: GameState) -> bool:
    """
    Final pitch at San Francisco.
    Returns True if investors buy in.
    """
    print(term.deepskyblue1("\n🎤 Final Demo Day Pitch —  Dinesh is presenting...🙏\n"))

    success_chance = 0.4

    if state.morale > 65:
        success_chance += 0.2
    elif state.morale < 40:
        success_chance -= 0.2

    if state.bugs >= 8:
        print(term.firebrick1("💥 Too many bugs. The demo crashes instantly 🌋"))
        return False

    if state.bugs > 5:
        success_chance -= 0.3

    if random.random() < success_chance:
        print(
            term.magenta2(
                "🚀 The demo is flawless! Investors are impressed 💰 Funding is coming your way! 🤑"
            )
        )
        return True

    print(term.firebrick1("💥 The demo crashes 😖 The team falls short... 🎻"))
    return False
