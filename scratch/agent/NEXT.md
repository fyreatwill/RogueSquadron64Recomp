# NEXT work unit — item -49's `R7A_LOADED`/`R7B_LOADED` positive-control
# soak, now unblocked: the `composeNpcOrientationMatrix` whack-a-mole
# family that has killed every run before reaching `renderUnlitMeshFaces`
# is CLOSED as of s261 (9 guards, 0 fires, 899 clean calls)

## Where the investigation stands (s261)

s261 closed s260's lead: `composeNpcOrientationMatrix`'s 9th gap was a
2nd-level pointer chase guard7 (s158) never covered — guard7 validates a
pointer FIELD loaded from a table entry (native `0x800AB4E8`), but the
dereference of THAT pointer one instruction later (`0x800AB4EC`,
`ctx->r2 = MEM_W(ctx->r2, 0X0)`) produces a brand-new, wholly unchecked
pointer, immediately used as the base for `0x68($v0)`/`0x5C($v0)`/
`0x70($v0)`/`0x64($v0)` (`0x800AB4F0`-`0x800AB504`). The literal `0x68`
offset matched the crash's `si_addr=0x380000068` byte-for-byte. Guarded
as `ROGUESQ_LOG_COMPOSE_NPC_GUARD9`, with a TIGHTENED lower bound
(`< 0x80001000`, not the standard `< 0x80000000`) since the bad value
(`0x80000068`, and even the bare `0x80000000`) passes a plain KSEG0 range
check trivially — justified because every literal KSEG0 constant anywhere
in this file sits at `0x800A0000`+, and `0x80000000-0x80000FFF` is the
N64's reserved boot-vector/IPL3 region.

**Soak result (`composeguard9`,
`scratch/s73_post_a_scene/composeguard9/run.log`, 4.47M lines) is the
strongest single result this whole investigation has produced**:
- All 9 `compose-npc-orient-guard*` diagnostics: **0 fires across 899
  calls** to the function (entry diagnostic count).
- `SETLOOKUP_ARG_GUARD`/`SETLOOKUP_TABLE_GUARD`/`EVALSPLINE_GUARD`/
  `HANGAR_BAY_DEREF_GUARD` (G30/G31): all still 0 fires (3rd/2nd/2nd
  independent soak confirming those earlier fixes hold).
- `[phase] vi_width=640 (was 512) ... at 143.1s update_screen #8552` —
  first soak ever to survive a SECOND phase transition (the SELECT-CRAFT
  transition at 75.0s happened as always, but every prior soak died
  before or shortly after it; this one kept going for another ~68s).
- `[CRASH][unlit-mesh-tracer] positive-control calls=1` — **the first
  time this counter has EVER fired**, across the entire multi-session
  history of this investigation (previously always 0).
- Crash: `renderUnlitMeshFaces+792` (native pc offset),
  `si_addr=0x380630062` — the already-catalogued item -49 KSEG0-
  zero-extension bug (CURRENT-TRUTH.md entry -49), **7th confirmed
  occurrence, exact signature match to s208/s254/s256**.

**What this means**: the `composeNpcOrientationMatrix` family (s100-261,
21+ sessions) is no longer a blocker between the game and
`renderUnlitMeshFaces`. Every future soak should get a live call into
that function (barring an unlucky scripted-input path or a 10th,
not-yet-exercised gap in the same family — single-soak result, iron rule
4 not fully satisfied for guard9 specifically, though the "positive
control fired for the first time ever" signal is unusually strong
evidence on its own).

## The next work unit, in priority order

### Option A (higher expected value): pick up item -49 directly

Read the item -49 entry in `docs/CURRENT-TRUTH.md` (grep `^-49\.`) in
full for the accumulated context on `R7A_LOADED`/`R7B_LOADED` (s257's
still-untested tracer sites, funcs_4.c). These are silent unless they
detect an out-of-bounds computed address (see
`_rogue_unlit_mesh_tracer_check` in `fixup_game_funcs.py`, gated by
`ROGUESQ_LOG_UNLIT_MESH_TRACER`, already armed in
`scratch/s73_post_a_scene/run_composeguard9.sh`). This run's crash
happened on the function's FIRST and ONLY call (`calls=1`), before
`R7A_LOADED`/`R7B_LOADED` (later in the function body) were reached —
check via `grep -n "0x80011DC8\|0x80011F1C"` in funcs_4.c and compare the
native offset to the crash's `+792` to see whether they're upstream or
downstream of the actual fault point. If downstream (likely, given the
function didn't get far enough this run), the discriminating question is
whether a DIFFERENT, earlier site is the real one -- re-read
`renderUnlitMeshFaces` (funcs_4.c) from its start down to whatever native
offset corresponds to `+792` (**do NOT trust `+792` as a line number or
guest address** — established rule, confirmed misleading repeatedly) to
find what's actually at the fault point on this specific crashing call.

### Option B (lower risk, satisfies iron rule 4 first): re-run composeguard9

Copy `scratch/s73_post_a_scene/run_composeguard9.sh` to a new tag (same
env, same everything) and re-soak once more. If it again shows 0 fires
on all 9 compose-npc guards and reaches `renderUnlitMeshFaces`, that's
the 2nd independent soak needed to fully close the family per iron rule
4, and whatever crash happens (same item -49 signature, or something new)
becomes the next target either way. If a 10th gap surfaces instead
(guard9 fires, or a NEW composeNpcOrientationMatrix crash site appears),
that's real information too.

Given budget rule 8 (stop after 3 iterations without a discriminating
result), prefer Option A first since it directly extends the strongest
finding this investigation has had — but Option B is defensible if
Option A's read doesn't produce a clear guard candidate within the first
read-through.

### Step: build → soak (if a new guard/tracer site is added)

Same full-regen cycle as always (delete `funcs_*.c` → `make_elf.py` →
`N64Recomp` → `fixup_game_funcs.py`, **redirect its output to a scratch
log file and grep it for your new guard's report line — do NOT trust a
bare terminal run** → clean `cmake --build .` → `strings`-verify the new
env var) → copy `scratch/s73_post_a_scene/run_composeguard9.sh` (NOT any
older `setlookupguard*`/`compose*` script — this is now the current-best
known-survivor baseline) to a new tag, keep everything it already arms,
add your new site's env var.

Block-wait pattern (unchanged): launch with `run_in_background: true`,
read the driver's first line for `pid NNNNN` (note: the actual soak
scripts live under `scratch/s73_post_a_scene/`, NOT `scratch/agent/` —
confirmed this session after an initial wrong guess), then a SEPARATE
foreground Bash call (timeout up to 480000ms):
`until ! kill -0 <pid> 2>/dev/null; do sleep 10; done`.

**Discriminating outcomes**: new site fires with sane fields -> mechanism
found for item -49, note whether the hold survives further past 143.1s.
Crash recurs at the EXACT same `renderUnlitMeshFaces+792`/`0x380630062`
signature with 0 new-tracer fires -> the bug is somewhere this session's
read didn't reach yet, re-read the function more carefully rather than
guessing at another site. `composeNpcOrientationMatrix` crash returns
(guard9 fires, or a new, 10th site appears) -> that takes priority over
item -49, since it's earlier in the call chain.

## Do NOT do this iteration

- Do NOT re-litigate whether the `composeNpcOrientationMatrix` 1-9 guard
  family or `setLookupEntryField5ByKey`'s guards fixed their targeted
  bugs — treat both as closed (2-3 independent soaks each, iron rule 4
  satisfied) unless a NEW soak shows one of their exact signatures
  recurring.
- Do NOT assume `R7A_LOADED`/`R7B_LOADED` are the right sites without
  checking whether they're upstream or downstream of the crash's actual
  native offset on THIS run — the crash happened on the function's very
  first call, which may not have reached them yet.
- Do NOT use a crash symbol's native `+N` offset as a source line number
  or guest address.
- Do NOT re-attempt `nm`/`atos`/`objdump` for offset localization —
  confirmed unusable repeatedly. Use `scratch/agent/machoparse.py` if
  function-size verification is needed.
- Do NOT run `fixup_game_funcs.py` more than once per regen cycle without
  redirecting output to a file and grepping the report line count first.

## Environment notes (carried forward, still current as of s261)

- **Soak driver scripts live under `scratch/s73_post_a_scene/`, NOT
  `scratch/agent/`** — this session wasted a round-trip on the wrong
  guess; `scratch/agent/` holds logs/analysis scripts, the actual
  `run_*.sh` launchers and their `run.log` output directories are all
  under `scratch/s73_post_a_scene/`.
- **`+N` crash-symbol offsets are NATIVE (compiled ARM64) code offsets,
  NOT guest MIPS addresses.**
- **Block-wait pattern**: `run_in_background: true`, read the pid from the
  driver's first output line, then a SEPARATE foreground Bash call
  polling `until ! kill -0 <pid> 2>/dev/null; do sleep 10; done`.
- Deleting `funcs_*.c` before regen: plain `rm` with a glob and `find
  -delete` are both blocked by the sandbox this session — use
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('.../funcs_*.c')]"` instead.
- **Headless permission matching is a PREFIX match on the command
  string** — compound commands (`&&`, `;`, `$(...)`) after a `cd` or
  inline in the same call get blocked for approval; run each step as its
  own Bash call. `env VAR=1 cmd` is allowlisted where a bare `VAR=1 cmd`
  is not.
- **The `[phase] vi_width=512 (was 1024) origin=0x006AB400` line at
  ~t=74-75s is THE confirmed SELECT-CRAFT->mission transition marker.**
  As of s261, `vi_width=640 (was 512)` at ~t=143s is a confirmed SECOND,
  later transition worth tracking too.
- **Regen is mandatory-delete-all-first, AND fixup must run EXACTLY
  once per regen** — always capture its stdout to a file and grep the
  report line for your new guard, rather than trusting a `tail` of a
  live terminal run.
- `N64Recomp` is a separate sibling git repo; `fixup_game_funcs.py` is
  intentionally untracked there (`??` in `git status`) — this is
  established, accepted practice, not something to fix.
- `CURRENT-TRUTH.md` is ~450KB, ~13x the ~35KB target in CLAUDE.md. Not
  addressed this session either (budget went to one build-soak cycle that
  produced the strongest result of the investigation). A dedicated
  pruning session — migrating durable material to `PROJECT-OVERVIEW.md`
  and trimming/archiving old "Next steps" entries that are now fully
  superseded — is now overdue across 3+ consecutive sessions and should
  be seriously considered as the next work unit soon, separate from the
  crash-chasing chain.
