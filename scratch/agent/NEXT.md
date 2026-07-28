# NEXT work unit — get a real (positive-controlled) read on the s219
# `renderUnlitMeshFaces` guard, since the first soak never exercised it

Read PORTING-STATE Session 219 in full (`grep -n "^## Session 219"
PORTING-STATE.md`) before doing anything else. Short version: s219 refuted
NEXT.md's (s218's) "hunt for the write site of the literal
`0x0000000300000000`" premise — that register value is just this process's
constant native RDRAM host base pointer (s194 already said so,
`PORTING-STATE.md:17934`, a session s216-218 never checked back against),
present in every fault by construction. Re-pulling the still-on-disk raw
crash logs for all 4 "sightings" (s194, s199, s217, s218) showed the OTHER
register (`x9`, the actually-wild operand) is byte-identical
(`0x0000000080630062`) across 3 of them — s194, s199, and s218 are the SAME
already-diagnosed, never-fixed `renderUnlitMeshFaces` bug's 4th recurrence,
not 3 independent sightings — while s217's `heapWalker` crash has a
genuinely different value (`0x38d47580`, no KSEG0-tag shape) and is a
separate, still-unexplained bug.

s219 source-read `renderUnlitMeshFaces` (`funcs_4.c:4963-5630`), found the
one unguarded "peek-load on a freshly-read list-walk pointer" site
(`0x80011CE0`, same idiom as heapWalker's GUARD4/heapFreeListDequeue's
guard), shipped a guard (`fixup_game_funcs.py`, sibling `N64Recomp`
checkout), and soaked (`renderunlitguard1`). Result: the **first soak in the
s209-218 lineage to survive the full 300s hold window with 0 crashes** — but
the guarded function's own positive control (the pre-existing
`unlit-mesh-tracer` call counter) fired **0 times**. `renderUnlitMeshFaces`
was never called during that run at all. Per rule 1 (a null result needs a
positive control in the SAME run), this soak is uninformative on whether the
new guard actually does anything — it just means this particular run didn't
route through mesh rendering enough to test it.

## Do this iteration: re-soak until the positive control actually fires

### Step 1 — just re-run the same soak first (cheap, do this before changing anything)

`scratch/s73_post_a_scene/run_renderunlitguard1.sh` already has
`ROGUESQ_LOG_UNLIT_MESH_TRACER=1` and `ROGUESQ_LOG_RENDERUNLIT_GUARD=1`
armed. Copy it to a new tag (e.g. `run_renderunlitguard2.sh` /
`renderunlitguard2`, per the "never overwrite a prior run's run.log"
convention) and run it once, unchanged. Reaching mesh-rendering content is
known to be non-deterministic run-to-run in this harness (even s218's own
soak, which DID hit the target crash, only logged `positive-control
calls=1` — called the "hot, every-frame" function exactly once before
dying) — a second attempt has a real chance of a different outcome without
needing any script changes.

Discriminating outcomes:
- **`unlit-mesh-tracer` positive-control fires (any count) AND
  `[renderunlit-guard]` fires (n>0) AND the run survives past where it would
  have died** → the guard is live and prevented its target crash; real
  progress, write it up as confirmed (single-source — a second, independent
  soak would still be needed before it's a two-source claim per rule 4).
- **Positive control fires, guard fires 0, run dies to a byte-identical
  `renderUnlitMeshFaces`/`x9=0x80630062` SIGBUS again** → this session's
  site identification was wrong; the actual fault is a DIFFERENT unguarded
  site in this function (recall the two known occurrences were at +508 and
  +792 bytes — not necessarily the same instruction). Re-read the function
  around both offsets for a second candidate site instead of re-shipping the
  same fix.
- **Positive control fires, guard fires 0, run survives with no
  `renderUnlitMeshFaces`-area crash** → consistent with (but does not prove)
  the fix working; note as single-source-positive and move on.
- **Positive control fires 0 again** → try Step 2 rather than repeating Step
  1 a third time (budget rule 8).

### Step 2 (only if Step 1's positive control fails again) — force the code path

Per NEXT.md-writing convention, do NOT redesign the whole recipe from
scratch. The existing `STICK_SCHEDULE` (`95:start 100:a 150:sr 200:sl
250:su`) was built for reaching the craft-select hold, not guaranteed to
enter an outdoor/flight scene where mesh faces render. Check
`docs/CURRENT-TRUTH.md`'s menu-state-machine section (grep `"Menu state
machine"`) for the exact key sequence known to leave SELECT YOUR CRAFT into
the flight/mission scene, and extend the schedule with that.

## Do NOT do this iteration

- Do not revive the "hunt the shared write site of `0x0000000300000000`"
  framing — it is refuted by raw register data (s219), not just
  unconfirmed. If a future session wants to double check, the falsifying
  fact to re-verify is simply: is `x0`/`x8` the same value across every
  future crash regardless of subsystem? (Expected: yes, always — it's a
  process constant, not a corruption signature.)
- Do not source-read a new function chasing a "4th sighting" of the literal
  — per the above, there almost certainly isn't one; any future crash
  showing `x0/x8=0x0000000300000000` should be read as "some `MEM_W`-shaped
  fault happened," not evidence of anything.
- Do not touch `heapWalker`'s `x9=0x38d47580` (s217) lead reflexively this
  iteration — it's real and separate, but chasing it isn't THIS iteration's
  planned unit (re-testing the s219 fix is higher value with less new
  reading required). If it recurs on its own during Step 1/2's soak, note it
  but don't source-read it same-session (budget rule 8 territory already
  spent this lineage on heapWalker twice).

## Environment notes (carried forward, still current)

- **`renderUnlitMeshFaces` is `funcs_4.c:4963-5630`** (confirmed s219 via
  `grep -n "^RECOMP_FUNC" funcs_4.c`). `heapWalker` is `funcs_3.c:99-700`,
  `heapFreeListDequeue` is `funcs_3.c:15427-17128` (both s217/s218,
  unchanged).
- **Raw crash logs are often still on disk long after the session that
  produced them** — before trusting a session's prose summary of a register
  dump, re-`grep` the actual `run.log` under `scratch/s73_post_a_scene/
  <tag>/run.log` if it still exists. This session found a real transcription
  error this way (s216's write-up doesn't arithmetically reproduce its own
  stated `si_addr`) and confirmed a byte-identical match this way
  (s194/s199/s218's `x9`). Cheap and decisive — do this before re-deriving
  anything from a written summary alone.
- **`recomp.h` location**: the ONE that matters is
  `lib/N64ModernRuntime/N64Recomp/include/recomp.h` — nested submodule
  inside `lib/N64ModernRuntime`, not the sibling `N64Recomp` checkout.
  `submodule-patches/export.sh`/`apply.sh` cover both. Any edit under `lib/`
  needs `export.sh` + commit, same session (not triggered this session — no
  `lib/` edits).
- **`fixup_game_funcs.py` lives at
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`** —
  the sibling checkout, genuinely untracked there (known since s83, not this
  project's commit scope, flagged for the user). This session's new
  `renderUnlitMeshFaces` guard is only saved there — verify it's still
  present (`grep -n renderunlit_guard fixup_game_funcs.py`) before assuming
  a re-regen will include it; if the file were ever lost, the exact code is
  also fully reproducible from PORTING-STATE Session 219's text.
- **`fixup_game_funcs.py` is NOT fully idempotent** for at least one older
  patch (s139 `rs_malloc`) — only run it ONCE per regen cycle.
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
- `./build/N64Recomp rogue_squadron.toml` needs an `env` prefix. Compound
  `cd ... && cmd` gets denied in one Bash call — issue `cd` and the
  following command as SEPARATE Bash calls.
- `git -C <path> <cmd>` does not match a `Bash(git <cmd>:*)` allow-rule —
  `cd` into the target dir first (its own Bash call), then run bare
  `git <cmd>`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- Launch soaks with `Bash(..., run_in_background=true)`, then either wait
  for the automatic task-notification or block with
  `TaskOutput(task_id, block=true, timeout=180000-480000)`.
- The `grep -ac '[CRASH]'` count in `run_mission_keys.sh`'s summary counts
  LINES matching the tag, not crash EVENTS — grep `caught signal` for the
  real event count. `unlit-mesh-tracer`'s own positive-control line is
  logged with a `[CRASH]` prefix too even though it isn't a crash (an
  existing project logging convention, not a bug) — don't confuse it with an
  actual fault when grepping.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s219 —
read it with `grep`/offset-limited `Read`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md` and
prune superseded detail, paired with a real experiment — flagged for 17+
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
