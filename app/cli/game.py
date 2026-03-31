"""Main loop, end conditions, and CLI prompts."""

from __future__ import annotations

from app.gameplay.actions import debug, rest, travel
from app.models.state import GameState
from app.world.config import LOCATIONS, term


def check_end_conditions(state: GameState) -> None:
    """Set game over state from resource loss."""
    if state.cash <= 0:
        print()
        print("💸 You ran out of cash. The startup collapses 😭")
        state.is_over = True
        state.win = False
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

    if state.progress_index >= len(LOCATIONS) - 1:
        return


def show_player_status(state: GameState) -> None:
    """Print the current state to the CLI."""
    print()
    print(term.green3("\n===== Silicon Valley Trail ====="))
    print(f"{term.green3('Day:')} {term.green3(str(state.day))}")
    print(f"{term.green3('Location:')} {term.green3(state.current_location)}")
    print(
        f"💵 Cash: {state.cash} | ⛽️ Fuel: {state.fuel} | "
        f"🥳 Morale: {state.morale} | 👾 Bugs: {state.bugs}"
    )


def prompt_action() -> str:
    """Ask the player what to do this day."""
    print(term.green3("\nChoose an action:"))
    print("1) 🚗 travel  - move to the next location")
    print("2) 🥱 rest    - recover morale and refuel a bit")
    print("3) ⚡️ debug   - fix bugs but costs morale")
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
    """CLI: status → action → tick day → win/lose checks."""
    state = GameState(cash=start_cash, fuel=start_fuel, morale=start_morale)

    while not state.is_over:
        show_player_status(state)

        action = ""
        while not action:
            action = prompt_action()
            if not action:
                print(term.gold("⚠️ Invalid choice. Enter 1-travel, 2-rest, or 3-debug ⚠️"))

        if action == "travel":
            travel(state)
        elif action == "rest":
            rest(state)
        elif action == "debug":
            debug(state)

        state.day += 1
        state.sync_location()
        check_end_conditions(state)

    print(term.green3("\n\n=== Game Over ==="))
    if state.win:
        print(
            term.magenta2(
                "🙌 You reached San Francisco, met with investors and secured funding!!! The future is yours 🔮"
            )
        )
    else:
        print()
        print(term.deepskyblue1(" 🚗💨 Your run ended. One more iteration and you'll make it 🍀"))
