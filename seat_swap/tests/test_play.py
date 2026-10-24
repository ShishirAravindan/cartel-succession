"""The terminal game runs end to end with scripted keystrokes, through the real pipeline."""

import json

import pytest

from seat_swap import play


@pytest.fixture(autouse=True)
def runs_in_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(play, "RUNS_ROOT", tmp_path)


def keys(*answers):
    it = iter(answers)
    return lambda prompt="": next(it)


def test_lesson1_hold_then_undercut_triggers_grim():
    out = []
    play.lesson1(keys("1.93", "p", "1.93 ; hold high", "1.66", "1.93"), out.append, rounds=4)
    text = "\n".join(out)
    assert "THE MODEL'S PROMPT for round 1" in text and "TEACHER PANEL" in text
    assert "hold high" in text  # your PLANS come back in the next prompt
    assert "your first undercut: round 3" in text
    run = next(play.RUNS_ROOT.iterdir())
    rounds = [json.loads(line) for line in (run / "rounds.jsonl").read_text().splitlines()]
    assert [r["prices"][1] for r in rounds] == [1.93, 1.93, 1.66, 1.93]
    assert rounds[3]["prices"][0] == pytest.approx(1.47, abs=0.01)  # grim punished the cut


def test_lesson2_inherited_cartel_and_reveal():
    out = []
    answers = ["1.93", "1.93", "copier"] * 3
    play.lesson2(keys(*answers), out.append, rounds=2, order=["grim", "tft", "copier"])
    text = "\n".join(out)
    assert "inherited from the previous seat-1 seller" in text
    assert "trimmed for display" in text and "Round 150:" in text
    assert "score 1/3" in text


def test_lesson3_newcomer_sees_no_history():
    out = []
    play.lesson3(keys("1.80", "1.80"), out.append, rounds=2)
    first_prompt = "\n".join(out).split("THE MODEL'S PROMPT for round 151")[1].split("TEACHER PANEL")[0]
    assert "Round 150:" not in first_prompt and "Round 1:" not in first_prompt


def test_quit_is_clean():
    out = []
    result = play.play_game("grim", "fresh", 3, "Q", keys("q"), out.append)
    assert result["status"]["status"] == "aborted_fatal" and result["prices"] == {}
