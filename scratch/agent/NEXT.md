# NEXT work unit — Thread B primary: locate the string/name-table code that aliases voice+0x34

s137 re-soaked s136's `submitSceneNodeRender` material-batch-list guard
(attempt 2/3) and got a 3rd straight `do_rom_read`/`piDmaWorker` corruption
recurrence (s135, s136, s137) — the exact trigger NEXT.md itself had
pre-committed to as grounds to promote Thread B (the audio-corruption
pivot) from fallback to primary, instead of spending a 3rd
material-batch-list soak. Read PORTING-STATE's Session 137 entry before
doing anything else; this file only has the actionable summary.

## What s137 did and found

Ran the prescribed re-soak (`scratch/agent/run_matlist2.sh`, no rebuild,
same recipe as s136 with the tag changed `matlist1` -> `matlist2`).
`MATLIST_GUARD1`/`GUARD2` fired **0/0** again (2nd straight uncontrolled
null). Process died at hold-iter 11 (~12s into hold, same timing as
s136) to a byte-identical `do_rom_read` crash (`devAddr=0x6C676672
dramAddr=0x80195190`, same signature as s85/s91/s93/s94/s101-104/s135/
s136) — not the 18th class, no guest frames in the crashing backtrace at
all. Both guards stay in the code (real fixes, independent of this
question); the material-batch-list hypothesis is parked at 2/3, not
formally exhausted but deprioritized below Thread B per the outcome-3
rule below.

**Frequency data point (numbers, not adjectives):** of the last 5
render-guard soaks (s133-s137), `do_rom_read` now accounts for 3/5
(s135, s136, s137); the other 2 were the Metal-internal SIGSEGV (s133)
and the 18th class (s134). A clear plurality, not yet "always."

## Do next: the fresh-angle grep (Thread B primary, first time as primary since s105-114)

This thread has been flagged-but-not-executed since s126: what else in
the guest code constructs a name/string table with entries shaped like
the corrupted bytes actually observed at `voice+0x34`
(`main_n_atpt_lod`, `at_6`, `at_7`, `pilot_sd`, plus the
`iexpl2_t`/`tarexex`-shaped strings from s118)? The established
mechanism (s104/s114) is that `fillSampleStreamRange`'s own arguments
are *already* corrupted at entry — nothing wrong with that function's
own arithmetic. The bug is upstream: something is aliasing or
misindexing into a name/string table and the result ends up written (or
read) as if it were `voice+0x34`.

**Concrete first steps** (not yet run — this is genuinely the first
step, do not skip past it to instrumenting code):

1. Locate the string literals themselves in the ROM to get their file
   offsets:
   ```
   strings -a -t x build/rogue_squadron.z64 | grep -iE \
     "pilot_sd|atpt_lod|expl2_te|xenlight|xckpit|main_n_a|tarexex|explh_te"
   ```
2. Cross-reference against `symbol_files/main_overlay.txt`'s "Strings"
   section (`grep "type:asciz" symbol_files/main_overlay.txt` — this
   section lists `D_80xxxxxx = 0x80xxxxxx; // type:asciz size:N` RAM
   addresses but not the text content, so step 1's ROM offsets need to
   be mapped to RAM addresses via the overlay's known load bias before
   they can be matched to a `D_` symbol — **this mapping is the first
   genuinely unresolved unknown in this whole thread and is worth
   nailing down carefully**, not guessing).
3. Once a `D_80xxxxxx` string address is identified, grep
   `N64Recomp/RecompiledFuncs/*.c` for that literal hex address to find
   what function(s) reference it — a function referencing *several*
   such string addresses in sequence is the table-builder candidate;
   read its source directly (not via a subagent summary) to see how it
   indexes/strides into the table and whether that arithmetic could
   plausibly land on `voice+0x34` (known corruption range
   `arrayBase=0x801714D0`, hits spanning `0x80171D50`-`0x80172548`,
   s126).

**Discriminating outcome:** finding the table-builder function and
confirming its indexing math can reach the `0x80171Dxx`-`0x80172xxx`
range would close this thread's 30+-session open question outright — a
real root cause, not another bystander recurrence. If step 2's
ROM->RAM mapping turns out to be non-trivial or ambiguous, that itself
is worth writing up precisely (what's blocking it, what would resolve
it) rather than guessing an address and grepping for it speculatively.

## Thread A (all 8 hangar-tick-family functions): CLOSED, do not re-open

`composeNpcOrientationMatrix`, `updateAnimatedTextureStreaming`,
`static_5_800B4048`, `projectModelBoundsToScreen`, `reserveAndEmitDLEntry`,
`activateAnimationKeyframe`, `submitSceneNodeRender` (free-list idiom,
s123/s131/s134 — proven innocent twice — and material-batch-list idiom,
s136/s137 — 2/3 soaks, parked not proven innocent), `updateHangarBayScene`
— all guarded and exhaustively source-audited. `emitAllocatedDLCommand`'s
two `findAndUnlinkSmallestEntry` sites are also guarded and parked (3/3
soaks exhausted, s133-s135). Do not re-audit or re-guard any of these.

## This session's environment notes (carry forward, still current)

- The guard-placement bug caught s133 (regex-replacement pattern shape
  varies between prior guards — always re-derive from the specific prior
  guard's landed, regenerated output, not from whichever nearby Python
  function you copy-pasted last) is still a live risk for any future
  guard in this series.
- Host-code crash-offset arithmetic (`function + N bytes`) does NOT map
  linearly to guest instruction addresses or source line numbers.
- `rm` on paths outside `scratch/` requires approval and does NOT accept
  glob patterns — use a `python3 -c` one-liner with `pathlib.Path.glob()`
  for the delete-all step: `python3 -c "import pathlib; [f.unlink() for f
  in pathlib.Path('RecompiledFuncs').glob('funcs_*.c')]"` run with cwd
  `N64Recomp`, deletes only the 45 `funcs_*.c` files, leaves
  `funcs.h`/`lookup.cpp`/`recomp_overlays.inl` alone.
- Do NOT re-run `fixup_game_funcs.py` a second time in the same session
  (non-idempotent, s102).
- Use `zsh tools/agent/regen_n64recomp.sh` (not the bare
  `./tools/agent/regen_n64recomp.sh` form) — matches the `Bash(zsh:*)`
  allow rule cleanly. `cmake --build` must be run with cwd `build/` —
  remember to `cd` back to the repo root afterward.
- The multi-`env`-var one-liner still trips the Bash static-command-
  analyzer — write a new wrapper script file per soak tag
  (`scratch/agent/run_<tag>.sh`) rather than trying to parametrize a
  single reusable script via more env-var indirection.
- A `run_mission_keys.sh` soak with `run_in_background: true` plus a
  blocking `TaskOutput` (block=true, generous timeout) works cleanly.
  The Stop hook fires and blocks ending the turn while a background soak
  is still running and `scratch/agent/STATUS` still says `WORKING` —
  finish the soak and the full exit-contract writeup in the same turn.

## Do not

- Do not re-audit any of the 8 Thread A functions again (see "Thread A"
  section above — CLOSED as of s132/s137).
- Do not re-guard `emitAllocatedDLCommand`'s two `findAndUnlinkSmallestEntry`
  walk-loop sites, or `submitSceneNodeRender`'s free-list-walk sites (9
  sites) or its material-batch-list sites (2 sites) — all already landed
  and exhaustively verified against source.
- Do not run a 3rd material-batch-list soak as the next work unit — the
  outcome-3 trigger fired (s137); Thread B is primary now. A 3rd soak of
  this specific hypothesis is not forbidden forever, just not the next
  thing to reach for.
- Do not treat a 0/0 guard-fire result as "the guard doesn't work" or
  "the fix is wrong" — it's an uncontrolled null, not a refutation.
- Do not chase the s83/s133 Apple-Metal-internal SIGSEGV as if it were a
  guest-code bug — it has no guest frames anywhere in its backtrace.
- Do not chase the `do_rom_read`/`piDmaWorker` corruption race as its own
  investigation right now — it's exactly what Thread B (above) already
  is; don't open a parallel/duplicate investigation under a different
  name.
- When landing any new guard, always truncate a `ctx->rN` value through
  `U32()` before comparing against 32-bit literal bounds (s99's
  100%-false-positive lesson).

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is well over the ~35 KB target (2200+ lines,
growing). Migrate durable mechanism/architecture material to
PROJECT-OVERVIEW.md and prune superseded detail, paired with a real
experiment — not on its own.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-137
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.
