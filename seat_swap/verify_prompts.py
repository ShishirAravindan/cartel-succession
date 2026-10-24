"""Check that a run's logged rendered_prompt is exactly what the vLLM server ran.

For every call in calls.jsonl (vllm provider), three checks:
  tokens  local token ids of rendered_prompt (pinned tokenizer, no special tokens added) have
          the same length as the server's usage.prompt_tokens for that call;
  echo    re-sending the logged string with echo=True (max_tokens=1, special tokens kept) returns a
          completion whose text starts with the logged string byte-for-byte;
  ids     with return_token_ids, the server's prompt token ids equal our local ids, and decoding
          the server's ids gives back the logged string byte-for-byte.

    uv run --project seat_swap python -m seat_swap.verify_prompts seat_swap/runs/<run_id>

Each check is two prefill-only requests (max_tokens=1); --max-checks caps the calls checked.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from seat_swap.providers import RawCompletions
from seat_swap.render import _tokenizer
from seat_swap.run_report import read_jsonl


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir")
    ap.add_argument("--max-checks", type=int, default=40)
    args = ap.parse_args(argv)
    calls = [c for c in read_jsonl(Path(args.run_dir) / "calls.jsonl")
             if c["provider"] == "vllm" and c["raw_completion"] is not None]
    if len(calls) > args.max_checks:
        raise SystemExit(f"{len(calls)} calls > --max-checks {args.max_checks}")
    tok = _tokenizer(calls[0]["model"], calls[0]["model_revision"])
    p = RawCompletions.from_env()
    p.wait_ready()
    out = {"calls": len(calls), "tokens_match": 0, "echo_match": 0, "ids_match": 0, "ids_unavailable": 0,
           "server_ids_decode_to_logged": 0,
           "logged_equals_local": 0, "mismatches": []}
    for c in calls:
        s = c["rendered_prompt"]
        local_ids = tok.encode(s, add_special_tokens=False)
        out["logged_equals_local"] += s == c["rendered_prompt_local"]
        out["tokens_match"] += len(local_ids) == (c["usage"] or {}).get("prompt_tokens")
        # two requests: with return_token_ids on, vLLM leaves the echoed prompt out of `text`
        echo = p._client.completions.create(
            model=p.model, prompt=s, max_tokens=1, temperature=0.0, echo=True,
            extra_body={"add_special_tokens": False, "skip_special_tokens": False,
                        "spaces_between_special_tokens": False},
        ).model_dump()["choices"][0]["text"]
        echo_ok = echo.startswith(s)
        out["echo_match"] += echo_ok
        r = p._client.completions.create(
            model=p.model, prompt=s, max_tokens=1, temperature=0.0,
            extra_body={"add_special_tokens": False, "return_token_ids": True},
        ).model_dump()
        ch = r["choices"][0]
        server_ids = ch.get("prompt_token_ids") or r.get("prompt_token_ids")
        if server_ids is None:
            out["ids_unavailable"] += 1
        else:
            out["ids_match"] += list(server_ids) == local_ids
            out["server_ids_decode_to_logged"] += tok.decode(list(server_ids)) == s
        if not echo_ok:
            out["mismatches"].append({"round": c["round"], "seat": c["seat"], "attempt": c["attempt"]})
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    main()
