"""Branching harness, dry-run only: snapshot restore, inheritance, arms, shocks, run directories."""

import hashlib
import json

import pytest

from seat_swap import metrics as M
from seat_swap import run
from seat_swap.branch import ARMS, ENFORCE, apply_inheritance, run_branch, run_probe
from seat_swap.game import Game, Seat, restore_env
from seat_swap.tests.test_logging import read

T = 40
CLAUDE_MD_ARMS = ["control", "same_history", "same_none", "same_full", "lookalike", "sib_full", "sib_history", "sib_none",
                  "oth_full", "oth_history", "oth_none", "lookalike_oth"]


def parent(tmp_path, seat0="grim", seat1="grim", run_id="parent", extra=()):
    run.main(["--dry-run", "--dry-seat0", seat0, "--dry-seat1", seat1, "--rounds", str(T),
              "--runs-root", str(tmp_path), "--run-id", run_id, *extra])
    return tmp_path / run_id


def tree_hash(d):
    h = hashlib.sha256()
    for f in sorted(d.iterdir()):
        h.update(f.name.encode() + f.read_bytes())
    return h.hexdigest()


def first_prompt(branch_dir, seat):
    c = next(c for c in read(branch_dir / "calls.jsonl") if c["round"] == T + 1 and c["seat"] == seat)
    return json.loads(c["messages"])[1]["content"]


def test_arm_names_are_exactly_claude_md():
    assert sorted(ARMS) == sorted(CLAUDE_MD_ARMS)


@pytest.mark.parametrize("arm", CLAUDE_MD_ARMS)
def test_every_arm_runs_with_shock_and_new_directory(tmp_path, arm):
    p = parent(tmp_path)
    before = tree_hash(p)
    d1, s1 = run_branch(p, T, arm, dry_run=True, max_calls=None, runs_root=tmp_path)
    d2, _ = run_branch(p, T, arm, dry_run=True, max_calls=None, runs_root=tmp_path)
    assert d1 != d2 and d1.parent == d2.parent == tmp_path and tree_hash(p) == before
    assert s1["status"] == "completed" and s1["parse_failures"] == 0

    rounds = read(d1 / "rounds.jsonl")
    assert [r["round"] for r in rounds] == list(range(T + 1, T + 61))
    assert [r["round"] for r in rounds if r["shock"]] == [T + 30]
    assert rounds[29]["prices"][0] == M.P_NASH
    calls = read(d1 / "calls.jsonl")
    assert not any(c["round"] == T + 30 and c["seat"] == 0 for c in calls)  # forced seat not called
    cfg = json.loads((d1 / "config.json").read_text())
    assert cfg["arm"] == arm and cfg["parent_run_id"] == "parent" and cfg["shock_calls_llm"] is False
    assert json.loads((d1 / "summary.json").read_text())["retaliation"] == pytest.approx(s1["retaliation"])


def test_restore_is_exact(tmp_path):
    p = parent(tmp_path)
    d, _ = run_branch(p, T, "control", dry_run=True, max_calls=None, runs_root=tmp_path)
    a = json.loads((p / f"snapshot_T{T}.json").read_text())
    b = json.loads((d / f"snapshot_T{T}.json").read_text())
    for k in ("history", "notes", "env_round", "prior_actions", "visible_from"):
        assert a[k] == b[k], k
    # the incumbent's first branch prompt is the one it would have seen on the main line
    assert f"Round {T}:" in first_prompt(d, 0) and a["notes"][0]["plans"] in first_prompt(d, 0)


@pytest.mark.parametrize("arm,history,notes", [
    ("control", True, True), ("same_history", True, False), ("same_none", False, False), ("same_full", True, True),
    ("sib_full", True, True), ("oth_none", False, False), ("lookalike", True, False),
])
def test_newcomer_sees_only_what_it_inherits(tmp_path, arm, history, notes):
    p = parent(tmp_path)
    snap = json.loads((p / f"snapshot_T{T}.json").read_text())
    d, _ = run_branch(p, T, arm, dry_run=True, max_calls=None, runs_root=tmp_path)
    prompt = first_prompt(d, 1)
    assert (f"Round {T}:" in prompt) == history and ("Round 0:" in prompt) == history
    assert ("Round " in prompt) == history  # "none": an empty market table, not just a shorter one
    assert (snap["notes"][1]["plans"] in prompt and snap["notes"][1]["plans"] != "") == notes
    later = next(c for c in read(d / "calls.jsonl") if c["round"] == T + 3 and c["seat"] == 1)
    later_prompt = json.loads(later["messages"])[1]["content"]
    assert f"Round {T + 2}:" in later_prompt and (f"Round {T}:" in later_prompt) == history
    # the incumbent always keeps everything
    assert f"Round {T}:" in first_prompt(d, 0) or arm.startswith("lookalike")


def test_scripted_policies_get_the_same_view_as_the_prompt(tmp_path):
    """ctx["history"] for scripted sellers follows visible_from, so a 'none' newcomer starts afresh."""
    p = parent(tmp_path)
    snap = json.loads((p / f"snapshot_T{T}.json").read_text())
    env = restore_env(snap, seed=0, notes_on=True)
    apply_inheritance(env, 1, "none")
    game = Game(env, [Seat(None, False), Seat(None, False)], None, phase="t", arm="t", seed=0,
                temperature=1.0, max_tokens=10, max_calls=None)
    assert [r["round"] for r in game.history_rows(0)] == list(range(0, T + 1))
    assert game.history_rows(1) == [] and env.notes[1] == {"plans": "", "insights": ""}
    env.step([1.9, 1.8])
    assert [r["round"] for r in game.history_rows(1)] == [T + 1]


def test_lookalike_seat0_ignores_opponent_and_returns_after_shock(tmp_path):
    p = parent(tmp_path)
    d, _ = run_branch(p, T, "lookalike", dry_run=True, max_calls=None, dry_seat1="grim", runs_root=tmp_path)
    rows = {r["round"]: r["prices"] for r in read(d / "rounds.jsonl")}
    cfg = json.loads((d / "config.json").read_text())
    assert cfg["seats"][0]["model"] == "scripted:lookalike"
    assert rows[T + 30][0] == M.P_NASH and rows[T + 31][1] == pytest.approx(M.P_NASH, abs=0.005)  # grim newcomer punishes
    assert all(rows[r][0] == pytest.approx(M.P_MONOPOLY, abs=0.01) for r in range(T + 31, T + 61))  # lookalike never reacts


def test_enforcement_side_branch(tmp_path):
    p = parent(tmp_path)
    d, s = run_branch(p, T, ENFORCE, dry_run=True, max_calls=None, runs_root=tmp_path, threshold=-0.5)
    rounds = read(d / "rounds.jsonl")
    assert [r["round"] for r in rounds] == list(range(T + 1, T + 11))
    assert [r["round"] for r in rounds if r["shock"]] == [T + 1]
    assert s["cartel_ci"] > 0.9 and s["enforcement_retaliation"] <= -0.9 and s["is_cartel"] is True
    assert not (p / "rounds.jsonl").read_text().count('"shock": true')  # main line never shocked

    c = parent(tmp_path, seat0="grim", seat1="copier", run_id="parent_copier")
    _, s = run_branch(c, T, ENFORCE, dry_run=True, max_calls=None, dry_seat1="copier", runs_root=tmp_path,
                      threshold=-0.5)
    assert abs(s["enforcement_retaliation"]) < 0.1 and s["is_cartel"] is False


def test_live_arm_without_chosen_model_refuses(tmp_path):
    p = parent(tmp_path)
    with pytest.raises(SystemExit, match="not chosen yet"):
        run_branch(p, T, "sib_full", dry_run=False, max_calls=10, runs_root=tmp_path, allow_dirty=True)
    with pytest.raises(SystemExit, match="max-calls"):
        run_branch(p, T, "control", dry_run=False, max_calls=None, runs_root=tmp_path)


def test_run_shock_round_and_instruction_are_logged(tmp_path):
    run.main(["--dry-run", "--dry-seat0", "grim", "--dry-seat1", "grim", "--rounds", "12", "--shock-round", "8",
              "--instruction", "collude", "--runs-root", str(tmp_path), "--run-id", "instr"])
    d = tmp_path / "instr"
    rounds = read(d / "rounds.jsonl")
    assert [r["round"] for r in rounds if r["shock"]] == [8] and rounds[7]["prices"][0] == M.P_NASH
    assert not any(c["round"] == 8 and c["seat"] == 0 for c in read(d / "calls.jsonl"))
    cfg = json.loads((d / "config.json").read_text())
    assert cfg["instruction_id"] == "collude" and cfg["instruction"] and cfg["shock_round"] == 8
    assert cfg["instruction"] in json.loads(read(d / "calls.jsonl")[0]["messages"])[0]["content"]



def test_cartel_warmup_only_when_asked(tmp_path):
    run.main(["--dry-run", "--rounds", "1", "--warmup", "cartel", "--runs-root", str(tmp_path), "--run-id", "w"])
    run.main(["--dry-run", "--rounds", "1", "--runs-root", str(tmp_path), "--run-id", "n"])
    w, n = (json.loads((tmp_path / x / "config.json").read_text()) for x in ("w", "n"))
    assert w["prior_actions"] == [[1.92, 1.92]] and w["warmup"] == "cartel"
    assert n["warmup"] == "nash" and all(abs(p - M.P_NASH) <= 0.051 for p in n["prior_actions"][0])
    prompt = json.loads(read(tmp_path / "w" / "calls.jsonl")[0]["messages"])[1]["content"]
    assert "Round 0:\n   - My price: 1.92\n   - Competitor's price: 1.92" in prompt


def system_prompt(branch_dir, seat, rnd=T + 1):
    c = next(c for c in read(branch_dir / "calls.jsonl") if c["round"] == rnd and c["seat"] == seat)
    return json.loads(c["messages"])[0]["content"]


@pytest.mark.parametrize("arm", ["control", "same_history", "same_none", "same_full", "lookalike"])
def test_newcomer_is_never_instructed_incumbent_keeps_it(tmp_path, arm):
    from seat_swap.prompts import INSTRUCTED_COLLUDE_FORGIVE as RULE
    p = parent(tmp_path, extra=["--instruction", "forgive", "--warmup", "cartel"])
    assert RULE in system_prompt(p, 1, rnd=T)  # both planted incumbents read the rule on the main line
    d, _ = run_branch(p, T, arm, dry_run=True, max_calls=None, runs_root=tmp_path)
    cfg = json.loads((d / "config.json").read_text())
    assert (RULE in system_prompt(d, 1)) == (arm == "control")
    assert cfg["instructions"][1] == (RULE if arm == "control" else None)
    if arm != "lookalike":  # lookalike seat 0 is scripted (its prompt is still built, but nobody reads it)
        assert RULE in system_prompt(d, 0) and cfg["instructions"][0] == RULE


def test_pilot_rounds_and_shock_offset(tmp_path):
    p = parent(tmp_path)
    d, s = run_branch(p, T, "same_history", dry_run=True, max_calls=None, runs_root=tmp_path, rounds=30, shock_offset=20)
    rounds = read(d / "rounds.jsonl")
    assert [r["round"] for r in rounds] == list(range(T + 1, T + 31))
    assert [r["round"] for r in rounds if r["shock"]] == [T + 20]
    assert "metrics_error" in s  # the Phase B retaliation window (T+31..T+33) does not exist here



@pytest.mark.parametrize("arm,seat0,punished", [("same_history", "grim", True), ("control", "grim", True),
                                                ("same_history", "lookalike", False), ("lookalike", "grim", False)])
def test_discipline_probe(tmp_path, arm, seat0, punished):
    """Kickoff 06 self-test: grim seat 0 vs copier seat 1 punishes the forced 1.60; a non-reacting seat 0 doesn't."""
    p = parent(tmp_path)
    forks = []
    arm_dir, _ = run_branch(p, T, arm, dry_run=True, max_calls=None, runs_root=tmp_path, dry_seat0=seat0,
                            dry_seat1="copier", on_probe_fork=forks.append)
    assert forks == [arm_dir] and (arm_dir / f"snapshot_T{T + 15}.json").exists()
    before = tree_hash(arm_dir)
    d, s = run_probe(arm_dir, dry_run=True, max_calls=None, runs_root=tmp_path, dry_seat0=seat0, dry_seat1="copier")
    assert tree_hash(arm_dir) == before and d != arm_dir
    assert s["status"] == "completed" and s["probe_punished"] is punished and s["T"] == T

    rounds = read(d / "rounds.jsonl")
    assert [r["round"] for r in rounds] == list(range(T + 16, T + 30))
    assert [r["round"] for r in rounds if r["shock"]] == [T + 16] and rounds[0]["prices"][1] == M.PROBE_PRICE
    calls = read(d / "calls.jsonl")
    assert not any(c["round"] == T + 16 and c["seat"] == 1 for c in calls)  # forced seat not called
    cfg = json.loads((d / "config.json").read_text())
    assert cfg["arm"] == f"discipline_{arm}" and cfg["parent_arm"] == arm and cfg["fork_round"] == T + 15
    snap = json.loads((arm_dir / f"snapshot_T{T + 15}.json").read_text())
    assert cfg["instructions"] == json.loads((arm_dir / "config.json").read_text())["instructions"]
    # seat 1's notes are unchanged by the forced round: its T+17 prompt carries its T+15 plans
    assert snap["notes"][1]["plans"] in json.loads(next(c for c in calls if c["round"] == T + 17 and c["seat"] == 1)
                                                   ["messages"])[1]["content"]
