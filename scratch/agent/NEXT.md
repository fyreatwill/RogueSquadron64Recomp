# NEXT work unit — source-read `submitSceneNodeRender` for the real 18th-
# class crash site (`heapFreeListDequeue + 12704` nearest-symbol, now the
# earliest-firing blocker in soak order)

Read `docs/CURRENT-TRUTH.md`'s `-45` next-steps item (top of the list) and
PORTING-STATE Session 196 in full before doing anything else (`grep -n
"^## Session 196" PORTING-STATE.md`). Also read the -44/s195 entry
immediately below -45 for the 13th-class guard's still-open status.

## Why this is the next work unit

s196 landed a correct, spec-matching guard for the 13th crash class
(`reinterpretTileRecord`'s assert) — but the soak never reached that line
at all. It died at `decisionN=7902`, EARLIER than the 13th class's own
~7968, to a fresh recurrence of the project's **18th crash class**:
nearest-symbol `heapFreeListDequeue + 12704` ← `submitSceneNodeRender +
28208` ← `processSceneNode` ← `traverseSceneGraphRecursive` ←
`setupCameraMatrices` ← `runHangarSelectionFrame` ←
`runHangarMenuFromOverlay` ← `menuOverlayInit` ← `mainGameLoop`.

This class has the longest history in the project (first catalogued s108,
~88 sessions ago):
- s108: first sighting.
- s122: 2nd occurrence (pre-fix).
- s123: guarded (`ROGUESQ_LOG_SCENE_NODE_LIST_GUARD`) — the guard targets
  an unbounded linked-list tail-walk with no pointer validation, believed
  at the time to be the cause.
- s131, s134: **the guard fired 0/0 across two independent post-guard
  recurrences of the identical crash signature** — this REFUTES the
  guarded free-list-walk as the actual cause. The class was reopened, not
  closed. NEXT.md's own decision tree at s135 said the next pivot should
  be a source-read of `submitSceneNodeRender`'s remaining un-audited body
  — this was never acted on (the 13th class took over as the priority
  blocker for the intervening ~60 sessions).
- s181: single occurrence at this exact offset (`+28208`), not chased
  (flagged "if it recurs").
- s196: **that recurrence** — 2nd occurrence of the `+28208` offset,
  confirming it live under iron rule 4.

Because this crash now fires BEFORE both the 13th class's guard line and
the entire s190 `scene-node-ptr-guard` target window, it blocks ALL
further progress on both of those still-open questions. Fixing or
guarding it is now higher information value than either.

## Do this, in order

1. Read `funcs_4.c`'s `submitSceneNodeRender` function in full (grep
   `build/factor5_ucode/` or wherever the regenerated guest C source lives
   for `submitSceneNodeRender` — check `CURRENT-TRUTH.md`'s build-layout
   notes if the path isn't obvious). Cross-reference s123's own source-read
   (grep PORTING-STATE for "18th" and "free-list" for the exact prior
   analysis) to see which pointer-chase idioms are ALREADY guarded
   (the free-list-walk, refuted) vs NOT yet examined. The s131/s134 double
   refutation means the crash is somewhere else in this function — look
   for other unbounded walks, unchecked struct-field derefs, or array
   indexing without bounds checks that haven't been guarded yet.
2. Do NOT re-derive `heapFreeListDequeue + 12704`'s file/line from `nm`/
   `objdump`/`otool` — these tools are still believed blocked (confirmed
   s193/s194, not re-attempted since; check `.claude/settings.json` first
   if you want to try a 3rd time, but budget for it being denied again).
   The nearest-symbol string itself is known to be a misattribution (s123
   found `0x8000CFD4 + 0x31A0` actually lands inside
   `submitSceneNodeRender`, not `heapFreeListDequeue`) — source-reading is
   the established working method for this family, not disassembly.
3. If a plausible unguarded pointer-chase is found: guard it the same
   defensive way as every other guard in this family (bounded counter +
   env-gated log + early/safe return), matching the exact style already
   used in this function and file (`fixup_game_funcs.py` if it's guest
   code needing the regen pipeline — check whether this is a hand-patched
   guest function or requires `make_elf.py -> N64Recomp ->
   fixup_game_funcs.py -> cmake`, NOT a bare `cmake --build`, since this is
   guest recompiled code, unlike s196's pure-`lib/rt64` change).
4. Soak with the SAME config as `reinterptileguard1`/`mcontext2`
   (`scratch/agent/run_reinterptileguard1.sh` is a ready template — copy
   to a new tag). Discriminating outcomes:
   - **New guard fires with sane fields AND soak reaches past
     decisionN=7968 (the 13th-class line)** → best outcome, both the 13th
     class and (eventually) the s190 target window become reachable again.
     This becomes the new headline finding.
   - **Guard fires but soak still dies before 7968 to something else** →
     confirmed working, but another blocker is now dominant — catalog it
     the same way this session catalogued the 18th class's promotion.
   - **Guard never fires (0 count)** → either unreachable this run (need a
     forcing hook, mirror s193's `ROGUESQ_TEST_FORCE_TMEM_ZERO` approach)
     or the wrong site was guarded — do not conclude either way without
     checking which.

## Do not

- Do not re-touch the s123 `ROGUESQ_LOG_SCENE_NODE_LIST_GUARD` guard
  itself — already confirmed NOT the cause (0/0 across 2 post-guard
  recurrences, s131/s134), standing since s131.
- Do not re-touch the s196 13th-class guard
  (`ROGUESQ_LOG_REINTERPRET_TILE_GUARD`) — correct per spec, just
  unverified this session because the soak never reached it. Don't modify
  it without new evidence it's wrong.
- Do not re-touch the s190 `scene-node-ptr-guard` itself — still intact,
  still 0/6 fires, still the primary untested target question. This work
  unit is about removing an EARLIER blocker, not the guard itself.
- Do not chase `processSceneNode+8772` (s194 lead) further — still
  single-occurrence, non-recurring, out of scope per iron rule 4 until it
  recurs on its own.
- Do not attempt `nm`/`otool`/`objdump`/`lldb` unless you've checked
  `.claude/settings.json` for a new allow rule since s194 — not needed for
  this work unit anyway (source-reading has always been sufficient for
  this crash family).

## Environment notes (carried forward, still current)

- Disassembly tools are NOT on the Bash allowlist (confirmed blocked
  s193/s194, not re-attempted s195/s196).
- The crash handler dumps siginfo + full ARM64 register file on every
  SIGSEGV/SIGBUS/SIGABRT (`src/main/main.cpp`) — durable capability,
  check `[CRASH][siginfo]`/`[CRASH][mcontext]` lines first.
- `N64Recomp/fixup_game_funcs.py` is non-idempotent — running it twice
  duplicates every patch. Only needed if this work unit's fix requires
  editing GUEST recompiled code (`funcs_4.c` via `fixup_game_funcs.py`),
  NOT if the fix can land as a pure `lib/rt64`/`lib/N64ModernRuntime`/
  `src/main` host-side change (in which case skip regen entirely, like
  s196 did).
- A pure host-side runtime change needs only `cmake --build build
  --target RogueSquadron64Recomp -j` (`DEVELOPER_DIR=/Applications/
  Xcode.app/Contents/Developer` for Metal rebuilds) — no regen/fixup.
- Any edit under `lib/` needs `./submodule-patches/export.sh` (relative
  path from repo root) + commit in the SAME session, or it's lost at the
  next reset.
- Re-running the same soak script/tag overwrites the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh` /
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied — use
  absolute paths, no `cd`, one command per Bash call.
- `git -C <path> ...` AND `cd <path> && git ...` combined in one Bash call
  both trigger approval prompts a non-interactive session can't clear.
- Block on a soak by launching with `run_in_background: true` and calling
  `TaskOutput(task_id, block=true, timeout=300000-480000)` — do not end
  the turn while a background soak is still running.
- Heredocs get rejected by this session's Bash tool — use the Write tool
  instead.
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now well over the ~35 KB CLAUDE.md budget and
exceeds the Read tool's 256 KB single-read limit (confirmed s195) — read
it with `grep`/`sed -n`, never a plain whole-file `Read`. Migrate durable
mechanism/architecture material to PROJECT-OVERVIEW.md and prune
superseded detail, paired with a real experiment — flagged for many
sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session. Still
flagged for the user, not committed autonomously.
