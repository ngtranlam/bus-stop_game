"""Kiểm thử luật chơi của Campus Bus Challenge (chỉ logic, không mở cửa sổ).

Chạy từ thư mục campus-bus-challenge:
    python -m unittest discover -s tests -v
"""

import os
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

import FinalProject as game  # noqa: E402


def key_event(key):
    return pygame.event.Event(pygame.KEYDOWN, key=key)


def playing_state(seed=1):
    """Ván mới đang ở màn 1, lượt 1, trạng thái PLAYING."""
    return game.new_run(random.Random(seed))


def stop_at(state, offset):
    """Đặt tâm xe lệch `offset` px so với tâm trạm rồi nhấn Space."""
    moved = {**state, "bus_x": state["stop_center_x"] + offset}
    return game.handle_input(moved, [key_event(pygame.K_SPACE)])


def finish_feedback(state, rng=None):
    """Cho thời gian phản hồi/banner trôi qua đến khi về PLAYING hoặc GAME_OVER."""
    rng = rng or random.Random(2)
    for _ in range(5):
        if state["state"] in (game.PLAYING, game.GAME_OVER):
            return state
        state = game.update_game(state, 2.0, rng)
    return state


class GradeThresholdTests(unittest.TestCase):
    def test_boundaries(self):
        cases = [
            (0, game.PERFECT), (12, game.PERFECT),
            (12.01, game.GOOD), (32, game.GOOD),
            (32.01, game.OK), (65, game.OK),
            (65.01, game.MISS), (300, game.MISS),
        ]
        for distance, expected in cases:
            with self.subTest(distance=distance):
                self.assertEqual(game.calculate_grade(distance), expected)

    def test_left_and_right_offsets_give_same_grade(self):
        for offset in (0, 12, 12.01, 32, 32.01, 65, 65.01):
            with self.subTest(offset=offset):
                left = stop_at(playing_state(), -offset)
                right = stop_at(playing_state(), offset)
                self.assertEqual(left["result_grade"], right["result_grade"])
                self.assertEqual(left["result_points"], right["result_points"])

    def test_early_press_is_miss_and_costs_one_life(self):
        state = playing_state()
        state = game.handle_input(state, [key_event(pygame.K_SPACE)])  # xe còn ở x = -60
        self.assertEqual(state["result_grade"], game.MISS)
        self.assertEqual(state["lives"], 2)
        self.assertEqual(state["score"], 0)


class ComboTests(unittest.TestCase):
    def test_consecutive_perfect_points(self):
        state = playing_state()
        points = []
        for _ in range(7):
            state = stop_at(state, 0)
            points.append(state["result_points"])
            state = finish_feedback(state)
        self.assertEqual(points, [100, 120, 140, 160, 180, 200, 200])
        self.assertEqual(state["max_combo"], 7)

    def test_non_perfect_resets_combo(self):
        for offset in (20, 50, 100):  # GOOD, OK, MISS
            with self.subTest(offset=offset):
                state = stop_at(playing_state(), 0)
                state = stop_at(finish_feedback(state), 0)
                self.assertEqual(state["combo"], 2)
                state = stop_at(finish_feedback(state), offset)
                self.assertEqual(state["combo"], 0)
                state = stop_at(finish_feedback(state), 0)
                self.assertEqual(state["result_points"], 100)

    def test_combo_survives_level_change(self):
        state = playing_state()
        for _ in range(4):  # lượt 4 là lượt 1 của màn 2
            state = stop_at(finish_feedback(state), 0)
        self.assertEqual(state["level"], 2)
        self.assertEqual(state["combo"], 4)
        self.assertEqual(state["result_points"], 160)


class SpeedTests(unittest.TestCase):
    def test_speed_formula(self):
        self.assertAlmostEqual(game.calculate_speed(1), 260)
        self.assertAlmostEqual(game.calculate_speed(2), 299)
        self.assertAlmostEqual(game.calculate_speed(3), 343.85)

    def test_speed_is_capped(self):
        for level in range(1, 50):
            self.assertLessEqual(game.calculate_speed(level), 520)
        self.assertEqual(game.calculate_speed(6), 520)

    def test_huge_level_does_not_overflow(self):
        self.assertEqual(game.calculate_speed(10 ** 6), 520)
        self.assertEqual(game.calculate_speed(10 ** 100), 520)


class SingleResolutionTests(unittest.TestCase):
    def test_repeated_space_counts_once(self):
        state = {**playing_state(), "bus_x": playing_state()["stop_center_x"]}
        space = key_event(pygame.K_SPACE)
        state = game.handle_input(state, [space, space, space])
        state = game.handle_input(state, [space])
        self.assertEqual(state["score"], 100)
        self.assertEqual(state["total_stops"], 1)

    def test_auto_miss_once_when_bus_passes_zone(self):
        state = playing_state()
        state = {**state, "bus_x": state["stop_center_x"] + game.OK_LIMIT - 1}
        state = game.update_game(state, 0.05, random.Random(3))
        self.assertEqual(state["state"], game.RESULT)
        self.assertEqual(state["result_grade"], game.MISS)
        self.assertEqual(state["lives"], 2)
        # Space muộn hoặc thêm frame cập nhật không xử lý lại lượt này.
        state = game.handle_input(state, [key_event(pygame.K_SPACE)])
        state = game.update_game(state, 0.01, random.Random(3))
        self.assertEqual(state["lives"], 2)
        self.assertEqual(state["total_stops"], 1)

    def test_bus_stops_immediately(self):
        state = stop_at(playing_state(), 5)
        frozen_x = state["bus_x"]
        state = game.update_game(state, 0.3, random.Random(4))
        self.assertEqual(state["bus_x"], frozen_x)

    def test_bus_moves_with_delta_time(self):
        state = playing_state()
        moved = game.update_game(state, 0.05, random.Random(5))
        self.assertAlmostEqual(moved["bus_x"] - state["bus_x"], 260 * 0.05)

    def test_new_stop_is_inside_range(self):
        rng = random.Random(6)
        for _ in range(200):
            state = game.new_run(rng)
            self.assertGreaterEqual(state["stop_center_x"], game.STOP_MIN_X)
            self.assertLessEqual(state["stop_center_x"], game.STOP_MAX_X)
            self.assertEqual(state["bus_x"], game.BUS_START_X)


class LevelAndLivesTests(unittest.TestCase):
    def test_three_results_start_next_level(self):
        state = playing_state()
        for offset in (0, 100, 20):  # Miss cũng tính là một lượt
            state = stop_at(finish_feedback(state), offset)
        state = game.update_game(state, game.RESULT_DURATION + 0.01, random.Random(7))
        self.assertEqual(state["state"], game.LEVEL_TRANSITION)
        self.assertEqual(state["level"], 2)
        state = finish_feedback(state)
        self.assertEqual(state["state"], game.PLAYING)
        self.assertEqual(state["stop_index"], 1)
        self.assertAlmostEqual(state["speed"], 299)
        self.assertEqual(state["lives"], 2)

    def test_transition_already_uses_new_level_speed(self):
        # Lỗi đã gặp: banner LEVEL 2 vẫn hiện tốc độ của màn 1 trên HUD.
        state = {**playing_state(), "stop_index": 3}
        state = game.update_game(stop_at(state, 0), 2.0, random.Random(10))
        self.assertEqual(state["state"], game.LEVEL_TRANSITION)
        self.assertAlmostEqual(state["speed"], 299)

    def test_last_life_lost_on_third_stop_is_game_over(self):
        state = {**playing_state(), "lives": 1, "stop_index": 3}
        state = stop_at(state, 200)
        self.assertEqual(state["lives"], 0)
        state = finish_feedback(state)
        self.assertEqual(state["state"], game.GAME_OVER)
        self.assertEqual(state["level"], 1)

    def test_lives_never_negative(self):
        state = playing_state()
        for _ in range(3):
            state = stop_at(finish_feedback(state), 200)
        self.assertEqual(state["lives"], 0)
        self.assertEqual(finish_feedback(state)["state"], game.GAME_OVER)


class StateMachineTests(unittest.TestCase):
    def test_enter_starts_new_run(self):
        state = game.new_game_state()
        self.assertEqual(state["state"], game.TITLE)
        state = game.handle_input(state, [key_event(pygame.K_RETURN)])
        self.assertEqual(state["state"], game.PLAYING)
        self.assertEqual((state["level"], state["lives"], state["score"]), (1, 3, 0))

    def test_space_on_title_does_nothing(self):
        state = game.handle_input(game.new_game_state(), [key_event(pygame.K_SPACE)])
        self.assertEqual(state["state"], game.TITLE)

    def test_pause_freezes_everything_and_resumes(self):
        for setup in (playing_state(), stop_at(playing_state(), 0)):
            with self.subTest(state=setup["state"]):
                paused = game.handle_input(setup, [key_event(pygame.K_p)])
                self.assertEqual(paused["state"], game.PAUSED)
                after = game.update_game(paused, 1.0, random.Random(8))
                self.assertEqual(after["bus_x"], setup["bus_x"])
                self.assertEqual(after["result_timer"], setup["result_timer"])
                resumed = game.handle_input(after, [key_event(pygame.K_p)])
                self.assertEqual(resumed["state"], setup["state"])

    def test_pause_during_level_transition(self):
        state = {**playing_state(), "stop_index": 3}
        state = game.update_game(stop_at(state, 0), 2.0, random.Random(9))
        self.assertEqual(state["state"], game.LEVEL_TRANSITION)
        paused = game.handle_input(state, [key_event(pygame.K_p)])
        after = game.update_game(paused, 5.0, random.Random(9))
        self.assertEqual(after["transition_timer"], state["transition_timer"])
        self.assertEqual(game.handle_input(after, [key_event(pygame.K_p)])["state"],
                         game.LEVEL_TRANSITION)

    def test_space_while_paused_is_ignored(self):
        paused = game.handle_input(playing_state(), [key_event(pygame.K_p)])
        state = game.handle_input(paused, [key_event(pygame.K_SPACE)])
        self.assertEqual(state["total_stops"], 0)

    def test_retry_resets_run(self):
        state = playing_state()
        state = stop_at(state, 0)
        state = {**finish_feedback(state), "lives": 1}
        state = finish_feedback(stop_at(state, 200))
        self.assertEqual(state["state"], game.GAME_OVER)
        state = game.handle_input(state, [key_event(pygame.K_r)])
        self.assertEqual(state["state"], game.PLAYING)
        for key, value in (("score", 0), ("lives", 3), ("level", 1), ("combo", 0),
                           ("max_combo", 0), ("total_stops", 0), ("perfect_count", 0),
                           ("stop_index", 1)):
            self.assertEqual(state[key], value, key)

    def test_escape_and_window_close_quit_from_every_state(self):
        states = [game.new_game_state(), playing_state(), stop_at(playing_state(), 0),
                  game.handle_input(playing_state(), [key_event(pygame.K_p)])]
        for state in states:
            with self.subTest(state=state["state"]):
                self.assertFalse(game.handle_input(state, [key_event(pygame.K_ESCAPE)])["running"])
                quit_event = pygame.event.Event(pygame.QUIT)
                self.assertFalse(game.handle_input(state, [quit_event])["running"])

    def test_quit_is_not_overridden_by_later_key_in_same_frame(self):
        title = game.handle_input(game.new_game_state(),
                                  [key_event(pygame.K_ESCAPE), key_event(pygame.K_RETURN)])
        self.assertFalse(title["running"])
        over = {**playing_state(), "state": game.GAME_OVER}
        quit_event = pygame.event.Event(pygame.QUIT)
        self.assertFalse(game.handle_input(over, [quit_event, key_event(pygame.K_r)])["running"])

    def test_handle_input_does_not_mutate_original(self):
        state = playing_state()
        snapshot = dict(state)
        game.handle_input(state, [key_event(pygame.K_SPACE)])
        self.assertEqual(state, snapshot)


if __name__ == "__main__":
    unittest.main()
