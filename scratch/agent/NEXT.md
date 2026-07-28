# NEXT work unit — force a schedule that actually exercises the two
# now-unconfirmed guards (renderUnlitMeshFaces s219, emitAllocatedDLCommand
# s221), rather than re-running either soak byte-identical again

Read PORTING-STATE Session 221 in full (`grep -n "^## Session 221"
PORTING-STATE.md`) before doing anything else. Short version: s221
source-read `emitAllocatedDLCommand` (funcs_3.c:2622-3210) hunting for the
unguarded idiom behind s220's hold-iter-1 crash, and found the function
ALREADY has a guard mechanism for it (`GUARD2`/`GUARD3`, from s133,
`fixup_game_funcs.py`'s `_emit_dl_guard2_sites`/`_emit_dl_guard3_sites`
tables) — but s133's own comment ("inlined here TWICE") undercounted: the
vulnerable idiom is inlined **three** times in this function, and s133 only
patched two of the three copies. The missing one
(`0x800086DC`/`0x800086E8`, skip-label `L_80008718`) is exactly s220's
crash shape. Added it as a third tuple to both tables, rebuilt clean
(delete-all-funcs → N64Recomp → fixup_game_funcs.py **once** → cmake
--build), soaked (`emitdlguard1`).

**Result: survived the full 300s hold window with 0 crashes — but EVERY
diagnostic fired 0 times**, including the brand-new guard site AND s219's
still-unconfirmed `renderUnlitMeshFaces` guard (`unlit-mesh-tracer`/
`renderunlit-guard`, now 0/0 across a 3rd soak). This is an uncontrolled
null per rule 1: real (no regression, cleanest run in the lineage), but
does NOT confirm either guard prevents anything. Two identical-schedule
attempts have now been spent on each of these two questions
(`renderunlitguard1`/`renderunlitguard2` for the first, this session's
`emitdlguard1` for the second) — budget rule 8 says stop repeating the
SAME unchanged soak and either change the approach or go get a
discriminating measurement a different way.

## Why this is the priority

Both `renderUnlitMeshFaces` and `emitAllocatedDLCommand` are scene-graph
leaf render functions (reached via `processSceneNode`/
`traverseSceneGraphRecursive`/`submitSceneNodeRender`). They should fire
CONSTANTLY once real mesh/flight content is on screen — the fact that
`unlit-mesh-tracer`'s own POSITIVE CONTROL (a plain call counter, not a
corruption check) has now been 0/0/0 across three separate soaks strongly
suggests these soaks are simply never reaching content-heavy rendering at
all, not that the guards are ineffective. The `STICK_SCHEDULE` used by
every soak since s213 (`"95:start 100:a 150:sr 200:sl 250:su"`) presses
`start` once at hold+95s to leave SELECT YOUR CRAFT into hangar-flight, then
only 4 more single key-taps over the next 155s. If flight/mesh content
needs more sustained stick input to actually render meshes (vs. sitting in
a black loading transition or a static camera-orbit shot), this schedule
may simply never reach the code paths under test.

## Do this iteration

### Step 1 — design a schedule that forces sustained post-leave activity

Re-read CURRENT-TRUTH's menu-state-machine section (search
`"Menu state machine"`) for what's known about the post-`95:start` timeline
(a Chapter-1 cutscene, then a graphics-task-submission stall class, then —
if ever reached — actual hangar-flight). Consider:
- Moving `95:start` EARLIER (e.g. `60:start`) to leave more of the 300s hold
  budget for whatever comes after, since the cutscene/stall window alone
  may consume a large chunk of the current 300s before real flight content
  would even begin.
- Adding a denser, SUSTAINED stick sequence after the leave point (e.g.
  repeating `sr`/`sl`/`su`/`sd` every 5-10s for the remainder of the hold,
  not 3 single taps 50-100s apart) to simulate actual flight control input
  that might be needed to keep the scene in a rendering (not idle/stalled)
  state.
- Increasing `HOLD_S` beyond 300 if the above still doesn't leave enough
  post-leave time.

Name the new tag distinctly (e.g. `emitdlguard2` or `schedulepush1`) and
keep `ROGUESQ_LOG_EMIT_DL_GUARD2`/`3`, `ROGUESQ_LOG_RENDERUNLIT_GUARD`,
`ROGUESQ_LOG_UNLIT_MESH_TRACER`, and all other existing diagnostics armed
(see `scratch/s73_post_a_scene/run_emitdlguard1.sh` for the full list to
carry forward).

### Step 2 — soak and read the SAME discriminating signal as before

The controlling metric is `unlit-mesh-tracer`'s own call-counter (the
existing positive control): if it STILL fires 0 times with a schedule
change specifically designed to push into content-heavy rendering, that's
now a 4th null and worth treating as a real, documented finding in its own
right ("these soaks structurally never reach mesh-rendering content, for a
reason independent of any single guard") rather than continuing to
individually re-test each guard. If it fires ANY nonzero count, check
`emit-dl-guard2`/`3` and `renderunlit-guard` alongside it in the same run —
that's the two-guards-at-once discriminating soak this NEXT.md is
proposing.

Discriminating outcomes:
- **`unlit-mesh-tracer` fires (n>0) for the first time ever** → soaks CAN
  reach mesh content with the right schedule; check the two guards'
  firing counts in the same run for the first real read on whether either
  actually intercepts anything.
- **`unlit-mesh-tracer` still 0 despite the schedule change** → strong
  evidence the blocker is NOT guard-coverage on any of these functions but
  something upstream (never reaching a state where meshes render at all,
  e.g. permanently stuck in the graphics-task-submission stall class from
  the menu-state-machine section, or a menu/state-machine transition that
  never completes). Next session should pivot to diagnosing THAT instead of
  continuing to source-read individual leaf functions.
- **Crash recurs (any kind)** → normal, not a refutation of either guard;
  note whether it's the SAME `emitAllocatedDLCommand`/`renderUnlitMeshFaces`
  signature (site identification wrong) or something else (uncontrolled
  null, as usual).

## Do NOT do this iteration

- Do not re-run `emitdlguard1` or `renderunlitguard1`/`2` byte-identical a
  3rd/4th time — both have had 2 identical-schedule attempts each now
  (budget rule 8).
- Do not source-read a 4th consumer of the `0x0000000300000000`/raw-KSEG0
  fault family reflexively — that family is well-characterized (s194,
  s219, s220, s221 all confirm it's a constant rdram-base literal plus an
  un-subtracted guest pointer, not a mystery). Only chase a NEW consumer if
  a soak's crash dump names one specifically.
- Do not revisit `heapWalker`'s still-open `x9=0x38d47580` lead (s217) —
  real and separate, not this iteration's unit.

## Environment notes (carried forward, still current)

- **`emitAllocatedDLCommand` is `funcs_3.c:2622-3210`**, three inlined
  copies of the free-list-walk idiom: `0x800086DC`/`E8` (r4, skip-label
  `L_80008718`, **newly guarded s221**), `0x800087D8`/`E4` (r4, skip-label
  `L_80008814`, guarded s133), `0x800088DC`/`E8` (r5, skip-label
  `L_80008918`, guarded s133). `renderUnlitMeshFaces` is `funcs_4.c:4963-
  5630` (guard shipped s219, still unconfirmed live). `heapWalker` is
  `funcs_3.c:99-700`, `heapFreeListDequeue` is `funcs_3.c:15427-17128`
  (both s217/s218, unchanged).
- **`fixup_game_funcs.py` is NOT idempotent — NEVER run it twice in the
  same session without a delete-all-funcs regen in between**, even just to
  pipe its output through a filter. If you need to inspect specific report
  lines, redirect the FIRST run's output to a file
  (`python3 fixup_game_funcs.py > /path/to/log.txt 2>&1`, using a path
  under this repo's `scratch/agent/` — writes outside the allowed working
  directories get blocked) and grep the file, never re-invoke the script.
  s221 violated this once, live, and caught it via a whole-tree label-
  duplication audit (`grep -oE '^L_[A-Za-z0-9_]+:$' funcs_*.c | sort |
  uniq -c`, flag anything >1 WITHIN a single file — note plenty of
  DIFFERENT functions in the SAME file legitimately reuse label text
  across function boundaries in this codebase, e.g. funcs_24/27/28/29/30,
  since C labels are function-scoped; that's not a bug, only a duplicate
  reachable from ONE source read (like the guard-generated labels checked
  here) is).
- **Raw crash logs are often still on disk long after the session that
  produced them** — `grep` the actual `run.log` under
  `scratch/s73_post_a_scene/<tag>/run.log` before trusting a prose summary
  of a register dump.
- **`recomp.h` location**: `lib/N64ModernRuntime/N64Recomp/include/
  recomp.h` — nested submodule inside `lib/N64ModernRuntime`.
  `submodule-patches/export.sh`/`apply.sh` cover both copies. Any edit
  under `lib/` needs `export.sh` + commit, same session (not triggered
  s219/s220/s221 — no `lib/` edits any of those sessions).
- **`fixup_game_funcs.py` lives at
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`** —
  the sibling checkout, genuinely untracked there (known since s83, not
  this project's commit scope, flagged for the user).
- The `[CRASH][pc-symbol]` diagnostic (dladdr on raw mcontext `pc`) is
  permanent, always-on, more precise than `backtrace_symbols_fd` (s213).
- Disassembly tools (`nm`/`otool`/`objdump`/`lldb`/`atos`) are ALL blocked.
  Source-level reasoning only.
- `-O0` Debug build, `RECOMP_FUNC` noinline, no LTO — dladdr resolving to
  function F means the fault is inside F's own body.
- `recomp.h`: `U32(val)` = `(uint32_t)(val)`; `gpr` = `uint64_t`; a legit
  KSEG0 `gpr` sign-extends, upper bits `0xFFFFFFFF`. Always check upper 32
  bits explicitly — a bare `U32()` check is blind to this corruption shape.
- `rm -f <glob>`/`find <dir> -delete` are blocked — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- `./build/N64Recomp rogue_squadron.toml` needs an `env` prefix and must run
  with cwd set to the `N64Recomp` checkout itself (use
  `tools/agent/regen_n64recomp.sh`). Compound `cd ... && cmd` gets denied in
  one Bash call — issue `cd` and the following command as SEPARATE Bash
  calls; redirecting output (`> file`) in the same call as a `cd` also gets
  denied — write output to a file via a separate, non-`cd`-prefixed call, or
  just don't redirect (the tool captures stdout either way for short runs).
- `git -C <path> <cmd>` does not match a `Bash(git <cmd>:*)` allow-rule —
  `cd` into the target dir first (its own Bash call), then run bare
  `git <cmd>`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- Launch soaks with `Bash(..., run_in_background=true)`, then block inline
  on the completion marker (`grep -q -- "--- done ---"` in a polling loop
  against the run's `run.log`) rather than ending your turn — the Stop
  hook fires on `scratch/agent/STATUS` as soon as your turn ends, even
  mid-soak.
- The `grep -ac '[CRASH]'` count in `run_mission_keys.sh`'s summary counts
  LINES matching the tag, not crash EVENTS — grep `caught signal` for the
  real event count.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s221 —
read it with `grep`/offset-limited `Read`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md` and
prune superseded detail, paired with a real experiment — flagged for 19+
sessions without action, escalating.

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope) — worth surfacing to the user directly.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.

`lib/rt64` still shows as modified in `git status` — pre-existing, not
investigated; still worth checking whether its patches are in sync with
`submodule-patches/rt64*.patch` before assuming this is normal
steady-state dirtiness.
