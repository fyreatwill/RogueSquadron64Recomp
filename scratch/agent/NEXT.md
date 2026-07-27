# NEXT work unit — guard the 10th crash class (s125)

s124 closed the 9th class (`updateAnimatedTextureStreaming`) cleanly:
source-read confirmed s89's characterization, guard landed
(`ROGUESQ_LOG_ANIM_TEX_STREAM_GUARD`), full delete-all regen + rebuild
clean, one soak — 0/0 guard fires, but the function's own entry
diagnostic was *also* 0/0 (never called this run at all), so this is
an untested guard on an unexercised path, not a proven-safe one. Read
PORTING-STATE's Session 124 entry before doing anything else; this
file only has the actionable summary.

## Two live threads — pick ONE, in this order

### Thread A (recommended): guard the 10th crash class

Same expected-value logic as s99-s124: 7 of the hangar-tick-family's
19 catalogued classes are now guarded (16th/12th/11th/14th/17th/18th/
9th), all landed cleanly, zero regressions introduced. Keep converting
the cheapest remaining ones.

**10th class**: SIGBUS in `static_5_800B4048` (unconfirmed real name —
a `main_overlay.txt` comment guesses "updateTextOverlayLookupEntry"
but that name is absent from the built `RecompiledFuncs/*.c`; treat as
unverified), first seen s90, reached via the known
`updateHangarBayScene` (`0x800AB658`) → `runHangarSelectionFrame` →
`runHangarMenuFromOverlay` → `menuOverlayInit` chain. Catalog entry
(`docs/CURRENT-TRUTH.md`, crash catalog list) characterizes it as
"unguarded `MEM_W` off `a1` (4 fixed-offset derefs)" — same family
shape as the 9th/11th classes. 1 occurrence only, never recurred —
guarding after exactly 1 occurrence has ample precedent (9th and 11th
were both guarded that way).

1. **Source-read the full function first** (do not trust the s90
   one-line characterization blind, same lesson s124 re-learned for
   the 9th). `grep -n 'static_5_800B4048' N64Recomp/RecompiledFuncs/funcs_41.c`
   to find its definition (s92 confirmed the entry diagnostic
   `ROGUESQ_LOG_HANGAR_ENTRY=1` already lives there). Read it start to
   closing brace: confirm which register holds the guest pointer
   (catalog says `a1`, verify against the actual arg-copy instruction,
   don't assume), every dereference site, and the real epilogue label
   (search for the `restore $ra` / stack-pop sequence near the end —
   same technique used for `L_8005425C` this session and `L_80066204`
   in s101).
2. **Land the guard following the `_anim_tex_stream_guard_patch`
   template exactly** (`N64Recomp/fixup_game_funcs.py`, search for that
   function name to copy the pattern — it's the most recently landed,
   freshest example): entry-point bounds check via
   `U32(ctx->rN) < 0x80000000u || >= 0x80800000u`, gated by a new env
   var (pick something like `ROGUESQ_LOG_HANGAR_ENTRY_GUARD` — note
   `ROGUESQ_LOG_HANGAR_ENTRY`, no `_GUARD` suffix, already exists as
   s90's entry-diagnostic flag; do not collide with it), `goto` to the
   real epilogue on failure. Mandatory: truncate through `U32()` before
   the bounds compare (s99's postmortem — skipping this gave a 100%
   false-positive guard once already).
3. **Full delete-all regen is mandatory** (recurring reminder —
   `N64Recomp` silently keeps stale output otherwise):
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
   `x3`, musyxKeyOnVoice `x8`, every prior guard/diagnostic `x1`)
   before trusting the build.
4. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8`
   — grep for `error:` explicitly, 0 expected.
5. One soak: `env ROGUESQ_LOG_HANGAR_ENTRY_GUARD=1
   PROBE_MODE=start_only HOLD_S=30 zsh
   scratch/s73_post_a_scene/run_mission_keys.sh s125guard 5 8`.
   A clean negative control (0 fires, no regression) is sufficient to
   land it — do not require a positive or executed control before
   accepting the guard (s99-s124's own precedent: several of them had
   neither at landing time, including s124 itself this session).

### Thread B (alternative, if A is somehow blocked): the audio-corruption pivot

The `voice+0x0` mystery (s105-123, now the single longest-running open
thread) still has an unidentified corruption source. s118's own reframe
("is the voice-array base pointer itself corrupted to point into some
other name table, and if so which one") is the right next question. H1
(zero-init) and H2 (asset-alloc coincidence) are now both refuted with
positive controls (s122, s123) — do not re-open either. A fresh angle:
grep the recompiled tree for what else constructs a name/string table
with entries shaped like `at_6`/`at_7`/`main_n_atpt_lod`/`pilot_sd` (the
exact strings s118's and s123's dumps captured) — that producer's
buffer address is the next coincidence candidate. This is a real
investigation, not a mechanical guard — expect it to take more than one
iteration; write the actual hypothesis table into this file before
running anything, per ITERATION.md's own requirement.

## Do not

- Do not re-soak any of the 7 guarded classes specifically to force a
  positive control (16th/12th/11th/14th/17th/18th/9th) — not required
  before landing, and per this family's history the crash that recurs
  next is as likely to be some *other* still-unguarded class, or the
  `do_rom_read` race itself, as any of these seven.
- Do not treat s124's 0/0 (unexercised) result as evidence the 9th
  class is fixed in any stronger sense than "guard is in place, never
  triggered because the buggy path wasn't hit this run" — if it
  recurs, the guard's own `ROGUESQ_LOG_ANIM_TEX_STREAM_GUARD` diagnostic
  will show it firing; if the crash itself recurs with the guard
  showing 0 fires, that would be a real signal the guard is
  mis-anchored and worth a dedicated look.
- Do not re-litigate H1 (zero-init, closed s122) or H2 (asset-alloc
  coincidence, closed s123, 3/3 attempts used, rule 8) for the
  `voice+0x0` mystery.
- Do not re-run the `songlifecycle` idx-vs-count soak shape — closed
  3/3, s121. Do not re-test the `shutdownAudioEngine` alias hypothesis
  as causal — refuted 2/2, s120. Do not re-litigate hypothesis (b)
  (`musyxInitVoiceFromSample` pointer-identity check) — closed s117-119.
- When landing any new guard, always truncate a `ctx->rN` value through
  `U32()` before comparing against 32-bit literal bounds (s99's
  100%-false-positive lesson, repeated in every guard since).
- Do not chase the `do_rom_read`/`piDmaWorker` corruption race
  opportunistically from a guard-landing soak — it's tracked as its
  own item (-1) in CURRENT-TRUTH's next-steps list, not something to
  re-diagnose in passing.

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
s90-124 (`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`).
Same posture as the `rogue_squadron64` sibling checkout flagged since
s54. Worth asking the user whether/how to commit that history.
