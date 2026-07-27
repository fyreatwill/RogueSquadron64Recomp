# NEXT work unit — guard the 9th crash class (s124)

s123 closed two things cleanly: (1) the 18th crash class
(`submitSceneNodeRender`'s free-list-walk loop) is now source-pinned and
guarded (`ROGUESQ_LOG_SCENE_NODE_LIST_GUARD`, clean 0/0 negative
control) — nearest-symbol attribution had pointed at `heapFreeListDequeue`
but the real crash PC was a label inside a completely different
function; (2) the H2 address-coincidence question for `voice+0x0`
corruption (does the corrupted content coincide with
`loadAssetAndIterateSubchunks`'s asset buffer?) got its first-ever
same-run positive control (29 `[voice-active-gate-nz]` fires) and is
now **REFUTED**, not just untested — 3/3 attempts used, rule 8 closed,
do not re-run this soak shape. Read PORTING-STATE's Session 123 entry
before doing anything else; this file only has the actionable summary.

## Two live threads — pick ONE, in this order

### Thread A (recommended): guard the 9th crash class

Highest expected value right now: convert another catalogued-but-
unguarded crash class into a guard, following the exact template that
just worked cleanly 5 times running (11th/12th/16th/17th/18th, all
landed, all clean negative controls, zero regressions introduced).

**9th class**: SIGBUS in `updateAnimatedTextureStreaming`
(`N64Recomp/RecompiledFuncs/funcs_11.c:13667`, real function, reached
via the `menuOverlayInit` hangar-tick chain), first seen s89. Catalog
entry (`docs/CURRENT-TRUTH.md`, crash catalog list) already
characterizes it as "unguarded `MEM_W` off `a0`" — the same shape as
the 11th class (`projectModelBoundsToScreen`, guarded s101). 1
occurrence only, never recurred — guarding on a single occurrence has
ample precedent (11th itself was guarded after exactly 1 occurrence).

1. **Source-read the full function first** (do not trust the s89
   one-line characterization blind — it was written mid-investigation,
   not from a dedicated read). Read `funcs_11.c` from line 13667 to its
   closing brace. Confirm: where `a0`/`ctx->r4` (or whichever register
   holds the guest pointer) is first assigned, every place it's
   dereferenced, and the function's real epilogue label (search for the
   `restore $ra` / stack-pop sequence near the end, same technique
   s101 used to find `L_80066204` for `projectModelBoundsToScreen`).
2. **Land the guard following the `_project_model_bounds_guard_patch`
   template exactly** (`N64Recomp/fixup_game_funcs.py`, search for that
   function name to copy the pattern): entry-point bounds check via
   `U32(ctx->rN) < 0x80000000u || >= 0x80800000u`, gated by a new env
   var (`ROGUESQ_LOG_ANIM_TEX_STREAM_GUARD` — note `ROGUESQ_LOG_ANIM_TEX_STREAM`,
   no `_GUARD` suffix, already exists as s90's entry-diagnostic flag;
   do not collide with it, pick a distinct name), `goto` to the real
   epilogue on failure. Mandatory: truncate through `U32()` before the
   bounds compare (s99's postmortem — skipping this gave a 100%
   false-positive guard once already).
3. **Full delete-all regen is mandatory** (NEXT.md's own recurring
   reminder — `N64Recomp` silently keeps stale output otherwise):
   ```
   python3 -c "
   from pathlib import Path
   import os
   base = Path('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs')
   for f in base.glob('funcs_*.c'): os.remove(f)
   "
   python3 /Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py
   zsh tools/agent/regen_n64recomp.sh
   python3 /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py
   ```
   Read the **full** fixup report, not just your own patch's line —
   confirm every other line's multiplicity is unchanged (audio gate
   `x3`, musyxKeyOnVoice `x8`, everything else `x1`) before trusting
   the build.
4. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8`
   — grep for `error:` explicitly, 0 expected.
5. One soak: `env ROGUESQ_LOG_ANIM_TEX_STREAM_GUARD=1
   PROBE_MODE=start_only HOLD_S=30 zsh
   scratch/s73_post_a_scene/run_mission_keys.sh s124guard 5 8`.
   A clean negative control (0 fires, no regression) is sufficient to
   land it — do not require a positive control before accepting the
   guard (s99-s123's own precedent: none of them had one at landing
   time).

### Thread B (alternative, if A is somehow blocked): the audio-corruption pivot

The `voice+0x0` mystery (s105-123, now the single longest-running open
thread) still has an unidentified corruption source. s118's own reframe
("is the voice-array base pointer itself corrupted to point into some
other name table, and if so which one") is the right next question, but
its most obvious test (compare against `musyxInitVoiceFromSample`'s
pointer) is a dead end — s119 found that function never fires on this
driven path, 0/0 across 2 soaks, closed. **Do not retry that.** A fresh
angle: grep the recompiled tree for what else constructs a name/string
table with entries shaped like `at_6`/`at_7`/`main_n_atpt_lod`/
`pilot_sd` (the exact strings s118's and s123's dumps captured) — that
producer's buffer address is the next coincidence candidate, not
`loadAssetAndIterateSubchunks` (now cleared) and not
`musyxInitVoiceFromSample` (already the zero-init writer, unrelated to
this content). This is a real investigation, not a mechanical guard —
expect it to take more than one iteration; write the actual hypothesis
table into this file before running anything, per ITERATION.md's own
requirement.

## Do not

- Do not re-run the asset-alloc/voice-gate co-occurrence soak
  (`ROGUESQ_LOG_ASSET_ALLOC` + `ROGUESQ_LOG_VOICE_ACTIVE_GATE` together
  to test coincidence with `loadAssetAndIterateSubchunks` specifically)
  — closed 3/3, refuted with a positive control, s123.
- Do not re-run the `songlifecycle` idx-vs-count soak shape — closed
  3/3, s121.
- Do not re-test the `shutdownAudioEngine` alias hypothesis as causal —
  refuted 2/2, s120.
- Do not re-litigate hypothesis (b) (`musyxInitVoiceFromSample`
  comparison as a pointer-identity check) — closed s117-119.
- Do not re-soak the `submitSceneNodeRender` guard specifically to
  force a positive control — not required before landing (see Thread A
  step 5), and per this family's history the crash that recurs next is
  as likely to be some *other* still-unguarded class as this one.
- When landing any new guard, always truncate a `ctx->rN` value through
  `U32()` before comparing against 32-bit literal bounds (s99's
  100%-false-positive lesson, repeated in every guard since).

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is over the ~35 KB target. Migrate durable
mechanism/architecture material to PROJECT-OVERVIEW.md and prune
superseded detail, paired with a real experiment — not on its own.

The crash catalog (`docs/CURRENT-TRUTH.md`, "Crash catalog" list) is
missing a table entry for the probable-20th class first mentioned s117
(`voicegate2`, SIGBUS via `menuOverlayInit` → `static_5_800C6854` →
`static_5_800AAD9C` → `static_5_800AB1C8`, 1 occurrence, never chased) —
worth adding when convenient, not urgent enough to spend a dedicated
iteration on by itself.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git
checkout, not a `lib/` submodule, with uncommitted changes across
s90-123 (`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`).
Same posture as the `rogue_squadron64` sibling checkout flagged since
s54. Worth asking the user whether/how to commit that history.
