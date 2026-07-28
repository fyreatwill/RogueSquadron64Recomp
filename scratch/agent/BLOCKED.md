# BLOCKED — s228 (2026-07-28), 3rd consecutive session on the same permission gate

## What's needed

A human needs to fix (or confirm/deny) the `.claude/settings.json` Bash
permission rules in this repo. This session found a specific, testable
root-cause hypothesis and a concrete one-line fix to try — see "Recommended
fix" below. This is not a request to just "look at it again"; it's a
specific config edit to test.

## What's already been tried (s226, s227, s228 — do not repeat)

- s226: `tools/agent/regen_n64recomp.sh` (the actual target script) denied
  3x with "This command requires approval", despite matching the
  `Bash(tools/:*)` allow rule verbatim.
- s227: ruled out "script-specific" (tried a different `tools/`-prefixed
  script, same failure) and "Bash entirely broken" (`grep`, `python3`,
  `pwd` all ran fine same session). Narrowed to the `Bash(tools/:*)` /
  `Bash(./tools/:*)` rule pair.
- s228 (this session): ran `tools/agent/stop_gate.sh --verify` again as
  Step 0 of the prior session's plan — **still fails identically**, 3rd
  session in a row, no change. Per this project's own budget rule (iron
  rule 8, applied to environment access rather than a hypothesis), did NOT
  retry a 4th time. Instead ran ONE new falsification test:

      build/idontexist_permcheck_s228 --help
      → "This command requires approval"

  `build/:*` is a DIFFERENT allow rule than `tools/:*`, targeting a binary
  that doesn't exist (so if permission had been granted, the shell would
  have said "command not found", not "requires approval" — the failure is
  confirmed to happen at the permission layer, before the shell ever runs
  the command). **This also fails**, which rules out "specific to the
  `tools/` rule" as the explanation and narrows it further: it's a whole
  CLASS of allow rules failing — every rule in `.claude/settings.json`
  shaped like `Bash(<dir>/:*)` (a bare directory name ending in a slash,
  immediately followed by `:*`) — while every rule shaped
  `Bash(<word>:*)` (a bare command word, no slash, e.g. `cmake:*`,
  `python3:*`, `git add:*`, `grep:*`) has been empirically confirmed
  working across all 3 sessions.

## Recommended fix (untested — needs a human to try it)

Compare the two rule shapes in `.claude/settings.json`:

    "Bash(cmake:*)"        <- WORKS (bare word, then :*)
    "Bash(git add:*)"      <- WORKS (two words, then :*)
    "Bash(tools/:*)"       <- FAILS (word ending in /, then :*)
    "Bash(build/:*)"       <- FAILS (word ending in /, then :*)

The working rules all match a command where the ruled prefix is itself a
complete "word" (a full command name or subcommand), immediately followed
by a space in the real command line — e.g. `cmake --build ...` has a space
right after `cmake`. The failing rules try to match a command where the
prefix is NOT a complete word — `tools/agent/stop_gate.sh` has no space
after `tools/`; the path continues immediately with `agent/stop_gate.sh`.

Hypothesis: Claude Code's `Bash(<prefix>:*)` syntax treats `:*` as "match
this exact command-word, then any argument after a space" — i.e. it is NOT
a raw string-prefix wildcard. For a genuine partial-string prefix (matching
anything that starts with `tools/`, whether or not there's a space right
after), the correct syntax is almost certainly the plain-glob form without
the colon:

    "Bash(tools/*)"
    "Bash(./tools/*)"
    "Bash(build/*)"
    "Bash(./build/*)"

**Ask the human to edit `.claude/settings.json`**, replacing the four
`:*`-suffixed directory rules above with the `*`-only form, then re-run
`tools/agent/stop_gate.sh --verify` (or any `tools/`-prefixed command) in
a fresh session. This is a 1-line-per-rule change, low risk (it only
affects what's auto-approved, it does not grant anything not already
intended — the existing rules already show clear intent to allow
`tools/` and `build/` execution), and directly tests the hypothesis above.

If this fix works, also apply it prophylactically to any other
`Bash(<dir>/:*)`-shaped rules that haven't yet been individually tested
(scan `.claude/settings.json` for the pattern), since they're likely to
share the same bug even though they haven't been hit yet.

## Falsification experiment (if a human wants to confirm the diagnosis first, before editing anything)

In an interactive (non-headless) Claude Code session with this exact
`.claude/settings.json`, run `tools/agent/stop_gate.sh --verify` or
`build/idontexist_test --help`:
- If it does NOT prompt for approval there → the bug is specific to the
  headless/autonomous-loop runner's approval pass-through, not the rule
  syntax itself. (Less likely given the `:*`-vs-`*` structural difference
  found above, but worth ruling out.)
- If it DOES still prompt there too → confirms the rule-syntax hypothesis;
  proceed with the settings.json edit above.

## Impact / what's on hold

- The `deref0` diagnostic (landed s226 in
  `N64Recomp/fixup_game_funcs.py`, same `ROGUESQ_LOG_CAMPOSE` patch site)
  is still unvalidated. It cannot be soak-tested until
  `tools/agent/regen_n64recomp.sh` can run, because the regen pipeline
  (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake`) is
  the only way to get new instrumentation into the built binary, and the
  `N64Recomp` step is itself invoked via `regen_n64recomp.sh`
  (`tools/`-prefixed).
- 3 consecutive sessions (s226, s227, s228) have made zero build/soak
  progress on the camera-freeze investigation as a direct result. This is
  now the single highest-value environment fix available — everything
  else in CURRENT-TRUTH's "Next steps" that requires a rebuild is blocked
  behind it.

## What is NOT blocked

Read-only investigation, doc updates, and analysis of already-captured
logs (e.g. `campose1`'s existing log from s224, `git log`/`git status`/
`git diff`/`grep`/`python3` work) all still function normally — only
commands whose first word is a bare directory name ending in `/` appear to
be affected. If a future session wants to make progress without the fix,
scan CURRENT-TRUTH's "Next steps" for anything answerable from existing
captured logs alone (none currently identified — flagging as worth a
specific check if this gate is still open next session).
