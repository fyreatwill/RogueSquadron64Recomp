# BLOCKED (s1891, 2026-08-17)

HYPOTHESIS-ID: vi1024-reachability-regression

s1888-s1890 established, characterized, and exhaustively code-audited the
VI-1024 reachability regression (8/8 fresh runs fail; four crash/stall
signatures; H1-flake refuted; a full content diff of every non-ledger file
between s844 and HEAD found no code-level explanation; the one real candidate,
`rs64_is_hangar_vi()`, was built into a same-binary env-toggle A/B and
refuted). This is the 4th consecutive iteration on this slug. Per
`tools/agent/ITERATION.md` iron rule 8 and s1890's own NEXT.md instruction,
a 4th run re-confirming the same stall is not new information — I am not
running it.

## What I need, from whom

1. **One machine-state snapshot, pasted or dropped as a file, from OUTSIDE
   this harness** (a human running these locally, not through Claude Code —
   `top`, `vm_stat`, `who`, `pmset -g therm`, `sysctl` are all denied by this
   session's permission policy, confirmed independently in s1889 and s1890):
   ```
   top -l 1 -n 0
   vm_stat
   who
   pmset -g therm
   sysctl -n hw.ncpu hw.memsize
   ```
   This tests H3-machine-state: is something external (thermal throttling,
   memory pressure, another process) causing the regression, rather than a
   code change in the s844-HEAD window (already ruled out by s1890's audit)?
   Drop the output at `scratch/agent/human_snapshot.txt` or paste it into the
   next session's prompt.

2. **A one-time `git submodule update` run inside a DISPOSABLE clone**
   (NOT this worktree — that command is denied here by command-string match
   regardless of working directory, and running it here would discard
   `lib/`'s uncommitted standing patches):
   ```
   git clone /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp /tmp/rs64-bisect-clone
   cd /tmp/rs64-bisect-clone
   git checkout ef7a0fb9   # s844, the last known-good commit for VI-1024 reachability
   git submodule update --init --recursive
   ```
   Leave that clone in place. A future iteration can then build and run the
   pre-s844 commit for comparison against HEAD under the identical
   `s790_postsec2_reachability.sh` recipe — the only way to literally bisect
   the regression, since the code-content audit (s1890) already found no
   candidate in the diff itself.

## What I already tried (do not re-attempt without new input)

- Full content audit, s844→HEAD, all non-ledger files (s1890) — closed.
- `rs64_is_hangar_vi()` env-toggle A/B (s1890) — built and refuted.
- `top`/`vm_stat`/`who`/`pmset -g therm`/`sysctl` inside this harness — all
  denied by permission policy (s1889, s1890, confirmed again implicitly this
  session by not re-attempting).
- `git submodule update` inside a fresh worktree — denied by command-string
  match independent of working directory (s1890).

## Falsifiable close condition

If, on the next iteration, neither (1) nor (2) has been supplied, the correct
action is still BLOCKED — not a 5th re-confirmation run. If either is
supplied, act on it directly (deeper H3 read from the snapshot, or the actual
bisect build/run from the disposable clone) rather than restarting analysis.
