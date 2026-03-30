"""
Test suite for Silicon Valley Trail backend (app.silicon_valley_trail_backend).

Uses unittest and mocks for CLI input, HTTP, and randomness so tests stay deterministic.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from app.silicon_valley_trail_backend import (
    LOCATIONS,
    GameState,
    check_end_conditions,
    debug,
    final_pitch,
    get_distance,
    get_weather,
    is_costco_location,
    is_restaurant_location,
    rest,
    travel,
    _event_debug_standard,
    _event_rest_mentor_call,
    _event_travel_flat_tire,
    _event_travel_roadwork,
    _event_travel_supply_drop,
)


class TestLocationHelpers(unittest.TestCase):
    def test_is_costco_location(self) -> None:
        self.assertTrue(is_costco_location("Santa Clara"))
        self.assertFalse(is_costco_location("San Jose"))

    def test_is_restaurant_location(self) -> None:
        self.assertTrue(is_restaurant_location("Palo Alto"))
        self.assertFalse(is_restaurant_location("Redwood City"))


class TestGameState(unittest.TestCase):
    def test_sync_location_clamps_and_matches_route(self) -> None:
        state = GameState()
        state.progress_index = 0
        state.sync_location()
        self.assertEqual(state.current_location, LOCATIONS[0])

        state.progress_index = 999
        state.sync_location()
        self.assertEqual(state.progress_index, len(LOCATIONS) - 1)
        self.assertEqual(state.current_location, LOCATIONS[-1])

        state.progress_index = -5
        state.sync_location()
        self.assertEqual(state.progress_index, 0)


class TestGetDistance(unittest.TestCase):
    def test_known_segment(self) -> None:
        self.assertEqual(get_distance("San Jose", "Palo Alto"), 24)

    def test_default_segment(self) -> None:
        self.assertEqual(get_distance("San Jose", "Santa Clara"), 18)


class TestGetWeather(unittest.TestCase):
    def _mock_response(self, temp_c: float) -> MagicMock:
        mock = MagicMock()
        mock.json.return_value = {"current_weather": {"temperature": temp_c}}
        return mock

    def test_api_cold_maps_to_fog(self) -> None:
        # ~50°F
        with patch(
            "app.silicon_valley_trail_backend.requests.get",
            return_value=self._mock_response(10.0),
        ):
            w = get_weather("San Jose", "Santa Clara")
        self.assertEqual(w["condition"], "fog")
        self.assertEqual(w["fuel_multiplier"], 1.1)

    def test_api_hot_maps_to_heat(self) -> None:
        with patch(
            "app.silicon_valley_trail_backend.requests.get",
            return_value=self._mock_response(32.0),
        ):
            w = get_weather("San Jose", "Santa Clara")
        self.assertEqual(w["condition"], "heat")
        self.assertEqual(w["fuel_multiplier"], 1.3)

    def test_api_mid_temp_maps_to_rain(self) -> None:
        with patch(
            "app.silicon_valley_trail_backend.requests.get",
            return_value=self._mock_response(18.0),
        ):
            w = get_weather("San Jose", "Santa Clara")
        self.assertEqual(w["condition"], "rain")

    def test_api_warm_uses_weighted_branch(self) -> None:
        with patch(
            "app.silicon_valley_trail_backend.requests.get",
            return_value=self._mock_response(24.0),
        ), patch(
            "app.silicon_valley_trail_backend.random.choices",
            return_value=["clear"],
        ):
            w = get_weather("San Jose", "Santa Clara")
        self.assertEqual(w["condition"], "clear")

    def test_fallback_on_request_failure(self) -> None:
        with patch(
            "app.silicon_valley_trail_backend.requests.get",
            side_effect=OSError("network"),
        ), patch(
            "app.silicon_valley_trail_backend.random.choice",
            return_value="fog",
        ):
            w = get_weather("San Jose", "Santa Clara")
        self.assertEqual(w["condition"], "fog")


class TestCheckEndConditions(unittest.TestCase):
    def test_out_of_cash_ends_game(self) -> None:
        state = GameState(cash=0)
        with patch("builtins.print"):
            check_end_conditions(state)
        self.assertTrue(state.is_over)
        self.assertFalse(state.win)

    def test_out_of_fuel_ends_game(self) -> None:
        state = GameState(fuel=0)
        with patch("builtins.print"):
            check_end_conditions(state)
        self.assertTrue(state.is_over)

    def test_zero_morale_ends_game(self) -> None:
        state = GameState(morale=0)
        with patch("builtins.print"):
            check_end_conditions(state)
        self.assertTrue(state.is_over)

    def test_low_cash_does_not_trigger_game_over_in_check(self) -> None:
        state = GameState(cash=10, fuel=50, morale=50)
        with patch("builtins.print"):
            check_end_conditions(state)
        self.assertFalse(state.is_over)


class TestTravel(unittest.TestCase):
    def _fixed_weather_clear(self) -> dict:
        return {
            "condition": "clear",
            "fuel_multiplier": 1.0,
        }

    def test_travel_advances_and_applies_passive_bugs(self) -> None:
        state = GameState(
            progress_index=0,
            cash=100,
            fuel=100,
            morale=50,
            bugs=0,
        )
        state.sync_location()

        with patch(
            "app.silicon_valley_trail_backend.get_weather",
            return_value=self._fixed_weather_clear(),
        ), patch(
            "app.silicon_valley_trail_backend.trigger_random_event",
        ), patch("builtins.print"), patch(
            "builtins.input",
            return_value="n",
        ):
            travel(state)

        self.assertEqual(state.progress_index, 1)
        self.assertEqual(state.current_location, "Santa Clara")
        self.assertEqual(state.bugs, 1)

    def test_final_leg_blocks_travel_if_insufficient_fuel(self) -> None:
        state = GameState(
            progress_index=len(LOCATIONS) - 2,
            cash=100,
            fuel=1,
            morale=50,
        )
        state.sync_location()

        expensive_weather = {
            "condition": "clear",
            "fuel_multiplier": 1.0,
        }
        with patch(
            "app.silicon_valley_trail_backend.get_weather",
            return_value=expensive_weather,
        ), patch(
            "app.silicon_valley_trail_backend.get_distance",
            return_value=100,
        ), patch("builtins.print"):
            travel(state)

        self.assertTrue(state.is_over)
        self.assertFalse(state.win)
        self.assertEqual(state.progress_index, len(LOCATIONS) - 2)


class TestRest(unittest.TestCase):
    def test_rest_adjusts_resources(self) -> None:
        state = GameState(cash=50, fuel=50, morale=40, bugs=3)
        with patch(
            "app.silicon_valley_trail_backend.trigger_random_event",
            return_value="",
        ), patch("builtins.print"):
            rest(state)

        self.assertEqual(state.morale, 50)
        self.assertEqual(state.fuel, 56)
        self.assertEqual(state.bugs, 2)
        self.assertEqual(state.cash, 38)

    def test_rest_skips_when_cannot_afford(self) -> None:
        state = GameState(cash=10, fuel=50, morale=40, bugs=3)
        with patch("builtins.print"), patch(
            "app.silicon_valley_trail_backend.trigger_random_event",
        ) as mock_ev:
            rest(state)
        self.assertEqual(state.morale, 40)
        self.assertEqual(state.cash, 10)
        mock_ev.assert_not_called()


class TestDebug(unittest.TestCase):
    def test_debug_skips_when_no_bugs(self) -> None:
        state = GameState(bugs=0)
        with patch("builtins.print") as mock_print:
            debug(state)
        mock_print.assert_called()

    def test_debug_blocked_when_too_poor(self) -> None:
        state = GameState(bugs=5, cash=3, morale=50)
        with patch("builtins.print"):
            debug(state)
        self.assertEqual(state.bugs, 5)


class TestFinalPitch(unittest.TestCase):
    def test_instant_fail_when_bugs_too_high(self) -> None:
        state = GameState(bugs=8, morale=80)
        with patch("builtins.print"):
            ok = final_pitch(state)
        self.assertFalse(ok)

    def test_success_when_random_favors(self) -> None:
        state = GameState(bugs=2, morale=70)
        with patch("builtins.print"), patch(
            "app.silicon_valley_trail_backend.random.random",
            return_value=0.0,
        ):
            ok = final_pitch(state)
        self.assertTrue(ok)


class TestEventEffects(unittest.TestCase):
    def test_flat_tire_effect(self) -> None:
        state = GameState(fuel=50, cash=50, morale=50)
        msg = _event_travel_flat_tire(state)
        self.assertIn("Flat tire", msg)
        self.assertEqual(state.fuel, 40)
        self.assertEqual(state.cash, 40)
        self.assertEqual(state.morale, 48)

    def test_roadwork_effect(self) -> None:
        state = GameState(fuel=50, morale=50, bugs=1)
        _event_travel_roadwork(state)
        self.assertEqual(state.fuel, 35)
        self.assertEqual(state.bugs, 3)

    def test_supply_drop_effect(self) -> None:
        state = GameState(cash=10, fuel=10, morale=10, bugs=5)
        _event_travel_supply_drop(state)
        self.assertEqual(state.cash, 25)
        self.assertEqual(state.fuel, 30)

    def test_debug_standard_effect(self) -> None:
        state = GameState(bugs=10, morale=50, cash=20)
        _event_debug_standard(state)
        self.assertEqual(state.bugs, 7)
        self.assertEqual(state.morale, 45)
        self.assertEqual(state.cash, 15)

    def test_rest_mentor_call(self) -> None:
        state = GameState(morale=30, bugs=5, cash=30)
        _event_rest_mentor_call(state)
        self.assertEqual(state.morale, 38)
        self.assertEqual(state.bugs, 3)
        self.assertEqual(state.cash, 20)


if __name__ == "__main__":
    unittest.main()
