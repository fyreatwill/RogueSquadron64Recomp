# NEXT work unit

## s404 recap

Not a maintenance iteration (CURRENT-TRUTH was 50,241 bytes at session start, still comfortably under
the 60,000-byte trigger). Continued item -249 at s400/s402/s403's proven n≈20 scale.

First found and fixed a **candidate-count bookkeeping bug**: the candidate-generation script has no
memory of prior probe verdicts, so NONE/AMBIGUOUS names stay in `main_overlay.txt` and re-appear at
the front of every future regenerated list. Regenerating printed 712, not the 692 NEXT.md expected
from pure `778−86` subtraction. Fixed with a new persistent skip-list,
`scratch/agent/m4_known_skip.txt` — **read this file and filter its names out before slicing any
future candidate batch**, or you'll re-probe `initObjectAnimAndDetail` /
`computeTrackedObjectWorldAnchor` / `claimSongSlotForCurrentHandle` / `handleCraftSelectInput` for
the 3rd-4th time for free.

Then took the next 20 real candidates (post-filter): all single-owner `mission` (10 CONFIRMED + 10
WEAK), applied, regenerated (positive control: unmapped-functions-skipped 717→697, exactly −20),
rebuilt clean, all 20 `nm`-confirmed present. The **mandatory live-verify caught a new deterministic
crash**: Bus error in `playerXwingInit+2068` (`last-guest-pc=0x80011088`), firing right after
`vi_width=512` was reached (~89.2s). A same-binary repeat run reproduced it byte-identically (2/2),
while the 4 most recent historical verify runs (different batches, same checkpoint) were 0/4 crashed.
**Reverted the batch surgically** (`scratch/agent/s404_revert.py`, name+address matched), rebuilt, and
re-verified: the reverted checkpoint reached `vi_width=512`→`640` cleanly (89.4s→118.3s, 0 crashes) —
a 5th consistent clean data point at that checkpoint. Confirmed sibling-repo symbol files are back to
exact parity with s403's checkpoint (candidate count 712, matching pre-batch).

**Net: item -249 unchanged at 86/778 done, 692 real remain.** No new relocations landed, but a real
regression was found, differentially confirmed, and reverted before it could land. Full detail:
`docs/CURRENT-TRUTH.md` item -253, `PORTING-STATE` Session 404.

The 20 held-back names + full writeup: `scratch/agent/s404_crash_batch_needs_bisection.txt`. **Do
NOT re-apply this batch as a whole** — one or more of these 20 corrupts something reachable from
`playerXwingInit`, but which one(s) is not yet isolated (none appear directly in the crash
backtrace, so if real this is downstream/indirect corruption).

## Next work unit: bisect the s404 crash batch (recommended), OR skip past it and continue at n=20

**HYPOTHESIS-ID: m4-main-overlay-phantom-functions** (iteration 10 under this slug). Iteration 9
(s404) produced a discriminating result (found+confirmed+reverted a regression) — not a stall, iron
rule 8 does not trigger a pivot.

### Option A (recommended if time allows): bisect the 20-name crash batch
Split `scratch/agent/s404_crash_batch_needs_bisection.txt`'s 20 names into two halves of 10 (file
order is fine — no need to re-probe destinations, all 20 are already CONFIRMED/WEAK:mission from
s404). Apply just the FIRST half (10 names) via `s400_apply_batch.py`, regen+rebuild, live-verify with
the exact same probe.sh invocation s404 used:
```
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 \
  zsh tools/probe.sh <outdir> 45 2
```
PASS = reaches `vi_width=512` at ~89s AND continues to `vi_width=640` at ~118s with 0 crashes (the
crash previously fired within a few seconds of the 512 reach, so don't stop watching the log right at
512 — that's exactly where the bug hid last time). If half 1 is clean, apply half 2 on top and repeat
the live-verify (now 20 relocated, matching s404's original attempt) — if THAT crashes, the culprit is
in half 2; if half 1 alone already crashes, narrow to n=5, then n=1 the same way. Once isolated to a
single name, that name goes into `m4_known_skip.txt` (or a new "known-bad, needs deeper investigation"
list) rather than being relocated, and the REST of the 20 (proven safe) get applied and folded into
item -249's done count. This directly grows the done count again once resolved.

### Option B (if short on time): skip past this batch, continue the n=20 progression elsewhere
Regenerate the candidate list, filter with `m4_known_skip.txt`, **also filter out all 20 names in
`s404_crash_batch_needs_bisection.txt`** (temporarily — don't lose them, don't relocate them), and
take the NEXT 20 real candidates after that. This keeps the main progression moving but defers root-
causing the s404 regression to a dedicated future session — only do this if Option A's extra
build+verify cycles don't fit this iteration's budget.

### Do NOT this iteration
- Re-apply the s404 batch as a whole without bisecting first.
- Scale batch size above ~20-25 — still deferred, still not this session's initiative to decide.
- Patch around the `playerXwingInit` crash without first isolating which relocation causes it — per
  the standing rule, revert-then-investigate, not patch-same-iteration.

### Reminder: sibling-repo commit rule (item -3)
Every batch's symbol-file edits land in `~/Documents/Tools/rogue_squadron64/symbol_files/*.txt`, a
SEPARATE git repo with its own uncommitted history. Do NOT commit there autonomously — ask the user
first, per the standing rule. This repo's commit only covers `scratch/agent/*` and the docs.

## Soak queue

None currently queued — each batch/bisection step gets its own live-verify run inline.

## Iteration budget

HYPOTHESIS-ID: m4-main-overlay-phantom-functions, iteration 10. s404 (iteration 9) was a genuine
discriminating result, not a stall. Continue either the bisection (Option A) or the skip-and-continue
progression (Option B) — both are legitimate continuations of the same thread.
