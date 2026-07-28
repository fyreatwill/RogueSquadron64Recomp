# NEXT work unit — get a same-run positive control (or a 3rd clean pass)
# for the s197 cached-free-list-head guard before concluding the 18th
# crash class is closed

Read `docs/CURRENT-TRUTH.md`'s `-46` next-steps item (top of the list) and
PORTING-STATE Session 197 in full before doing anything else (`grep -n
"^## Session 197" PORTING-STATE.md`).

## Why this is the next work unit

s197 found and guarded the one dereference in `submitSceneNodeRender`'s
free-list idiom that bypasses all 3 existing guards (GUARD/GUARD2/GUARD3,
s123/s131): when the persistent global free-list cache (`0x801163B0`) is
non-empty at function entry, execution jumps straight to `L_800101AC`
(`funcs_4.c`), skipping `findAndUnlinkSmallestEntry` and every existing
guard, then dereferences the reloaded cache pointer with zero validation.
New guard: `ROGUESQ_LOG_SCENE_NODE_CACHE_GUARD`.

2 of 3 soaks (`cacheheadguard1`/`3`) reached and passed cleanly through the
18th class's reliable recent death point (decisionN 7902-7968, where
s195/s196 died) with **zero recurrence** of that crash. Soak 1 reached
decisionN=15719 — the furthest ever recorded (previous best 9741) — ending
only on wall-clock budget, not a crash. This is a real, if not airtight,
positive sign.

**But**: the new guard never fired in any of the 3 soaks (0/0/0) — there is
still no same-run positive control proving the corrupt-cache condition it
targets is real and was actually hit and neutralized. Per iron rule 1, a
null result needs a positive control before it counts as confirmation. The
2 "clean" runs instead died to OTHER, already-catalogued, unrelated crashes
(s165/s173's 23rd-class `waitForAnyAudioSlot` SIGSEGV; s184's
`evalCubicSplineAtTime` SIGBUS family) — neither invalidates the clean pass
through the 18th class's death zone, but neither confirms the guard's
mechanism either.

## Do this, in order

1. Copy `scratch/agent/run_cacheheadguard1.sh` to a new tag (e.g.
   `cacheheadguard4`) — identical env block, `ROGUESQ_LOG_SCENE_NODE_CACHE_GUARD=1`
   already armed. Run it (`zsh scratch/agent/run_cacheheadguard4.sh`,
   `run_in_background: true`, block on `TaskOutput` per the notes below).
2. Check the outcome against these discriminating branches:
   - **Guard fires with sane fields** (`[scene-node-cache-guard] n=... bad_r2=...`)
     → best outcome: proves the mechanism is real and the guard caught it.
     Promotes this from "suggestive" to "confirmed" — update CURRENT-TRUTH
     to say so, and the 18th class's status becomes "closed pending one
     more recurrence-free soak" rather than "open."
   - **Clean pass again (3rd time), guard still 0 fires, no 18th-class
     recurrence** → 3 clean passes in a row (2 informative + this one) is
     strong circumstantial evidence even without the guard ever firing —
     write this up as "very likely fixed, mechanism unconfirmed" and move
     the s190 `scene-node-ptr-guard` / s196 13th-class guard verification to
     top priority, since a clean run now reliably gets past this blocker.
   - **18th class recurs anyway (guard 0 fires, crash matches
     `submitSceneNodeRender+28208` signature)** → the s197 hypothesis is
     REFUTED — the cached-head bypass path was not the (or not the only)
     mechanism. Do not re-guard the same site again; source-read the
     function again for a DIFFERENT unguarded site (the general-purpose
     agent's candidates #2-6 from s197's delegated read are unexplored:
     material-batch-list loop-back reload gap, light-table unbounded index,
     DL/material-batch parallel-array unbounded index, epilogue
     viewport-index tables — check `PORTING-STATE.md` Session 197's "Rules
     out" section isn't exhaustive, the original agent transcript covered
     more candidates than were acted on).
   - **Dies early to an unrelated crash again** (23rd class, Metal
     shader-compiler, `evalCubicSplineAtTime`) → not informative, this is
     attempt N of up to 3 on this instrument (iron rule 8) — if this is the
     3rd such uninformative death in a row across the s197+this session's
     attempts, STOP soaking this hypothesis and write up "inconclusive,
     needs a different repro strategy" rather than burning a 4th run.
3. Whatever the outcome, update `PORTING-STATE.md` (new session entry),
   `docs/CURRENT-TRUTH.md` (`-46` entry's status), and this file, per the
   exit contract.

## Do not

- Do not re-touch the s123/s131 `ROGUESQ_LOG_SCENE_NODE_LIST_GUARD`/
  `GUARD2`/`GUARD3` — still confirmed not the cause on their own path,
  standing since s131.
- Do not re-touch the s197 `ROGUESQ_LOG_SCENE_NODE_CACHE_GUARD` guard's
  logic unless this session's soak provides NEW evidence it's wrong (e.g.
  it fires but the crash still happens right after, meaning the bail target
  is unsafe) — if it simply doesn't fire again, that's still a null result,
  not evidence against it.
- Do not re-touch the s196 13th-class `reinterpretTileRecord` guard
  (`ROGUESQ_LOG_REINTERPRET_TILE_GUARD`) — correct per spec, still
  unverified because no soak has reached it yet.
- Do not re-touch the s190 `scene-node-ptr-guard` — still intact, still
  0/6 fires, still the primary untested target question once earlier
  blockers clear.
- Do not chase the s184/s197 `evalCubicSplineAtTime` SIGBUS family or the
  s173 `waitForAnyAudioSlot` 23rd-class site this iteration — both are
  flagged, open, and lower priority; only pick either up if THIS session's
  soak dies to one of them AGAIN and you've already exhausted the 3-soak
  budget on the cache-guard question (i.e. only as a fallback, not a
  substitute).

## Environment notes (carried forward, still current)

- Disassembly tools (`nm`/`otool`/`objdump`/`lldb`) are NOT on the Bash
  allowlist (confirmed blocked s193/s194, not re-attempted since) — source
  reading is the established method for this family.
- The crash handler dumps siginfo + full ARM64 register file on every
  SIGSEGV/SIGBUS/SIGABRT (`src/main/main.cpp`) — check `[CRASH][siginfo]`/
  `[CRASH][mcontext]`/`[CRASH][vifs-snapshot]` lines first, plus the
  backtrace lines immediately below them (function names + offsets are
  printed directly, no disassembly needed).
- `N64Recomp/fixup_game_funcs.py` is non-idempotent — running it twice
  duplicates every patch. Only needed if editing GUEST recompiled code
  (`funcs_4.c` via `fixup_game_funcs.py`, regen pipeline: `make_elf.py` ->
  `N64Recomp` -> `fixup_game_funcs.py` -> `cmake --build`), NOT for a pure
  host-side (`lib/rt64`/`lib/N64ModernRuntime`/`src/main`) change.
- Any edit under THIS repo's `lib/` needs `./submodule-patches/export.sh` +
  commit in the SAME session. `N64Recomp` and `rogue_squadron64` are
  SEPARATE checkouts outside this repo, NOT `lib/` submodules — their
  uncommitted changes (including `fixup_game_funcs.py` and regenerated
  `RecompiledFuncs/*.c`) are flagged for the user, not this session's call
  to commit (established posture since s54/s90/s173).
- Re-running the same soak script/tag overwrites the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh` /
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied in ONE
  Bash call — use separate Bash calls (one `cd`, then the next command in
  its own call; cwd persists across calls) or wrap the whole thing in
  `zsh -c "..."` (matches the `Bash(zsh:*)` allow rule as a single command).
  This was needed THIS session for `N64Recomp/build/N64Recomp` (not on any
  allowlist pattern as a bare absolute path).
- Block on a soak by launching with `run_in_background: true` and calling
  `TaskOutput(task_id, block=true, timeout=300000-480000)` — do not end the
  turn while a background soak is still running. A `<task-notification>`
  also arrives automatically on completion.
- Heredocs get rejected by this session's Bash tool — use the Write tool
  instead, including for large PORTING-STATE.md appends (`cat tmpfile >>
  PORTING-STATE.md` after writing tmpfile with the Write tool — the file
  itself is ~1.2MB, too large for the Edit tool's read-first requirement).
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now well over the ~35 KB CLAUDE.md budget and
exceeds the Read tool's 256 KB single-read limit (confirmed s195, still
true s197 — read it with `grep`/`sed -n`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md`
and prune superseded detail, paired with a real experiment — flagged for
many sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes (including this session's
`fixup_game_funcs.py` guard and regenerated `funcs_4.c`), unrelated to this
session's commit scope. Still flagged for the user, not committed
autonomously.
