# NEXT work unit

HYPOTHESIS-ID: item-270-generic-cache-guard-confirmation

## What changed session s434 — read this before picking a thread

s433's queued confirmation soak came back matching NEITHER of its two expected outcomes: a 3rd, new
crash (`last-guest-pc=0x80008928`, `emitAllocatedDLCommand`). Localizing it found the exact idiom
`lui $v0,0x8011; lw $v0,0x63B0($v0); lw $v0,0x0($v0)` (reload the persistent free-list cache-head
global `0x801163B0`, dereference with zero validation) — the SAME global 4 prior sessions
(s197/s266/s270/s271) had each bespoke-guarded exactly ONE reactive occurrence of. A full codebase
scan (`scratch/agent/s434_idiom_scan.py`) found **107 further unguarded occurrences**, 100% uniform in
register usage and downstream shape. Fixed all 107 in one generic regex-based patch
(`GENERIC_CACHE_GUARD` in `N64Recomp/fixup_game_funcs.py`). Regenerated, rebuilt clean, fixup report
confirmed exactly 107 patches applied. A live verification run (same probe schedule as s427-433, guard
diagnostic armed) completed the FULL 300s/250s-keys schedule with **0 crashes** — deeper/longer than
every run in the -261..-269 saga (all previously died 19s-172s) — but the guard also fired **0 times**,
so this is a promising single-source result WITHOUT a positive control (iron rule 1), not a confirmed
fix. Full detail: PORTING-STATE Session 434, CURRENT-TRUTH item -270.

## The work unit — consume the queued confirmation soak, then decide

A confirmation soak (`scratch/agent/soak_queue/s434_genericcacheguard_confirm.sh`) was queued and
should have run automatically between iterations. **Check `scratch/agent/SOAK-RESULTS.md` (tail) for
its verdict before doing anything else.** It reruns the identical schedule with
`ROGUESQ_LOG_GENERIC_CACHE_GUARD=1` armed. Four possible outcomes:

1. **`rc=0`, guard fired N>0 times, no crash** — positive control achieved. This is the outcome that
   actually confirms the fix: the guard demonstrably caught a wild head pointer and prevented a crash
   from it. Promote item -270 from "promising, single-source" to "confirmed" in CURRENT-TRUTH. Queue 1-2
   more confirmation runs (same recipe) before fully closing the item — two independent clean+fired runs
   is the two-source bar (iron rule 4).
2. **`rc=0`, guard fired 0 times, no crash (repeat of s434's own result)** — still no positive control.
   Each additional clean+silent repeat is weak reinforcing evidence but does NOT alone confirm the fix
   engaged (the crash could simply be nondeterministic and not always triggered by this exact key
   schedule). After 2-3 such repeats with zero fires, consider: the corrupting WRITE to `0x801163B0`
   itself may be rare/scene-gated rather than absent, and this key schedule may not reach the scene that
   provokes it. A discriminating next step: grep for what else in this project's session history reached
   FURTHER into gameplay than this schedule (deeper mission content) and try that schedule instead, since
   a schedule that never returns a guard fire cannot discriminate "fixed" from "untested."
3. **A NEW crash at a DIFFERENT, not-yet-guarded site** (check `last-guest-pc` against the 107 patched
   addresses in `RecompiledFuncs/funcs_3.c`/`funcs_4.c` grep for `GENERIC_CACHE_GUARD` context) — this
   family is closed (evidence: the 107-site sweep was exhaustive for this one exact idiom shape), the
   new crash is an unrelated bug; localize and start a fresh investigation the same way s434 did
   (`scratch/agent/s434_symrange2.py` is a reusable template for guest-PC-to-symbol localization).
4. **A crash at `0x801163B0` itself but through a DIFFERENT idiom shape** (e.g. a write instead of a
   read, or a deref pattern using a register other than `$v0`, or an offset other than the exact
   `0x63B0`/`0x0` pair) — the scan in `s434_idiom_scan.py` was scoped to one specific 2-instruction
   read-then-deref shape; a write-side idiom or a differently-shaped read would need its own scan.
   Re-read the crash's generated code directly (same method as s434) before assuming it's covered.

## Also worth checking once confirmation data exists

Item -263 (`tickWrappingTimerAccumulatorList`/`last-guest-pc=0x800547bc`, global `0x80137C84` — an
UNRELATED global from item -270's `0x801163B0`) still has not recurred since its single s426 sighting,
now 2 clean runs later (s433's own foreground run, s434's verification run). Still single-source, not
closeable, but worth reconsidering whether it was ever a real reproducible bug vs. a one-off — do not
actively chase it unless it recurs; the M3 idiom-class-audit priority (USER DIRECTIVE #3) does not
cover single, non-recurring sightings.

## Regen recipe (known-working s427-s434)

```
cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py
python3 -c "
import glob, os
for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c'):
    os.remove(f)
"
zsh ~/Documents/Tools/RogueSquadron64Recomp/tools/agent/regen_n64recomp.sh
python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py   # audit report for xN on every new patch, not "no changes"
cd ~/Documents/Tools/RogueSquadron64Recomp/build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8
```

`fixup_game_funcs.py` REFUSES to run a second time on the same generated files (checks for its own
`RS64_FIXUP_APPLIED` marker) — this is a safety net; if you see the refusal, you forgot to delete
`funcs_*.c` and regenerate first.

Live-run schedule (same as s423-434, known to reach the war-room/craft-select phase and now often runs
the full 300s without dying):
```
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_LOG_RUNNER=1 ROGUESQ_LOG_GENERIC_CACHE_GUARD=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
    PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
    PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start" \
    zsh tools/probe.sh <outdir> 300 2
```

## Sandbox notes (confirmed again s434)

Same as s433's notes (`lldb`/`otool -tV`/`find -delete`/plain `rm` with globs need interactive
approval — use `python3 -c` glob-delete; `atos` offsets need cross-checking against a symbol-range
walk before trusting large offsets; multi-line heredocs need the Write tool not Bash; foreground
`sleep`/loop-polling of a running game process is blocked by the sandbox's static checker — use
`TaskOutput` with `block=true` on the backgrounded run's task ID (from `run_in_background: true`) to
wait for it synchronously, or `Monitor` with an `until ! pgrep ...` condition for the async
notification path; a `for i in $(seq ...)` or `while ...; do sleep; done` loop with shell arithmetic on
a loop variable also trips the static checker — prefer `TaskOutput(block=true)` over any manual
poll loop entirely).

## Soak queue

- `scratch/agent/soak_queue/s434_genericcacheguard_confirm.sh` — queued this session, not yet run as of
  this writing. See "The work unit" above for how to read its verdict.
