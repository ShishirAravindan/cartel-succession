#import "../lib.typ": *

#heading(numbering: none, supplement: [Section])[LLM Usage Statement] <sec:llm>

The sellers we study (Qwen3-14B, Qwen3-8B, gpt-oss-20b) are the subjects of the experiments, not tools; this statement covers the LLMs that helped us do the research.

We used Anthropic's Claude heavily, in four roles:
- _Planning:_ Claude (Opus) sessions brainstormed and critiqued experimental designs and wrote the task brief for each step. The author discussed, approved, changed or rejected each one; every pre-registration, arm, threshold and spending decision was the author’s.
- _Engineering and analysis:_ Claude Code wrote nearly all of the code in `seat_swap/`, ran the experiments and did the first-pass analysis, logging each step in the repository.
- _Qualitative coding and critique:_ Claude (Sonnet) subagents coded the newcomers' transcripts blind to arm and outcome (@sec:notes) and wrote mock reviews from an economist's, an ML evaluator's and a policy reader's perspective, which we used to find weaknesses in the design and the claims.
- _Writing:_ The author set the report’s structure, framing and claims, and shaped the text over many rounds of drafting and critique. Claude drafted sections and proposed edits within that process. OpenAI’s GPT-6.1 (via Codex) was also used for clarity checks on drafts.

The author is responsible for every claim and errors are the author's.