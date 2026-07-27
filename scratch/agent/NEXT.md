# NEXT work unit — guard the 11th-catalog-remaining class or pivot (s126)

s125 closed the 10th class (`static_5_800B4048`) cleanly: source-read
refined s90's characterization (the live pointer is `ctx->r8`/`$t0`, a
copy of `$a1` made at function entry, not `ctx->r5` itself), guard
landed (`ROGUESQ_LOG_HANGAR_ENTRY_GUARD`), full delete-all regen +
rebuild clean, one soak — 0/0 guard fires, but the function's own
entry diagnostic was *also* 0/0 (never called this run at all), same
"untested guard on an unexercised path" caveat as s124's 9th class.
Read PORTING-STATE's Session 125 entry before doing anything else;
this file only has the actionable summary.

8 of 19 catalogued hangar-tick-family classes are now guarded:
16th/12th/11th/14th/17th/18th/9th/10th. Remaining unguarded, all
RT64-internal or one-off (not the cheap mechanical guard shape):
13th (`reinterpretTileRecord` assert, RDP path), 15th (`loadDrawState`
assert, RDP path, recurred once), 19th (Metal `MetalFramebuffer`
constructor SIGSEGV, render-thread path), plus the uncatalogued
probable-20th (`voicegate2`, s117, never source-read).

## Two live threads — pick ONE, in this order

### Thread A (recommended if a cheap guard target exists): source-read
the uncatalogued 20th class first

Before assuming the guard program has run out of cheap targets, do the
one thing never done for it: source-read the probable-20th class
first mentioned s117 — SIGBUS via `menuOverlayInit` →
`static_5_800C6854` → `static_5_800AAD9C` → `static_5_800AB1C8`, 1
occurrence, never chased. If it has the same "unguarded arg-pointer
deref" shape as the 9th/10th/11th/12th/14th/16th/17th/18th classes,
guard it the same way (grep the function names in the relevant
`funcs_*.c`, read to the closing brace, find the real epilogue label,
land a `U32()`-truncated bounds check + `goto`, gate behind a fresh env
var, full delete-all regen, soak with `PROBE_MODE=start_only
HOLD_S=30`). If it turns out to be RT64-internal or a different shape
(like 13th/15th/19th), catalog it properly (table entry in
CURRENT-TRUTH's crash catalog list) and fall through to Thread B.

### Thread B (alternative): the audio-corruption pivot

The `voice+0x0` mystery (s105-123, the single longest-running open
thread) still has an unidentified corruption source. s118's own reframe
("is the voice-array base pointer itself corrupted to point into some
other name table, and if so which one") is the right next question. H1
(zero-init) and H2 (asset-alloc coincidence) are both refuted with
positive controls (s122, s123) — do not re-open either. A fresh angle:
grep the recompiled tree for what else constructs a name/string table
with entries shaped like `at_6`/`at_7`/`main_n_atpt_lod`/`pilot_sd` (the
exact strings s118's and s123's dumps captured) — that producer's
buffer address is the next coincidence candidate. This is a real
investigation, not a mechanical guard — expect it to take more than one
iteration; write the actual hypothesis table into this file before
running anything, per ITERATION.md's own requirement.

## Do not

- Do not re-soak any of the 8 guarded classes specifically to force a
  positive control (16th/12th/11th/14th/17th/18th/9th/10th) — not
  required before landing, and per this family's history the crash
  that recurs next is as likely to be some *other* still-unguarded
  class, or the `do_rom_read` race itself, as any of these eight.
- Do not treat s124's or s125's 0/0 (unexercised) results as evidence
  those two classes are fixed in any stronger sense than "guard is in
  place, never triggered because the buggy path wasn't hit this run."
  If either recurs, its own `_GUARD` diagnostic will show whether the
  guard actually catches it or is mis-anchored.
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

`docs/CURRENT-TRUTH.md` is over the ~35 KB target (now well over —
1900+ lines). Migrate durable mechanism/architecture material to
PROJECT-OVERVIEW.md and prune superseded detail, paired with a real
experiment — not on its own.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git
checkout, not a `lib/` submodule, with uncommitted changes across
s90-125 (`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`).
Same posture as the `rogue_squadron64` sibling checkout flagged since
s54. Worth asking the user whether/how to commit that history.
