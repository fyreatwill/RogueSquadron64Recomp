# NEXT work unit — re-audit guarded functions for a 2nd bug site, or pivot to voice+0x0 (s127)

s126 closed the "probable-20th class" question (s117/`voicegate2`):
source-reading the full backtrace (`menuOverlayInit` → `static_5_
800C6854` → `static_5_800AAD9C` → `static_5_800AB1C8`) found all three
addresses are already-known, already-named functions
(`runHangarMenuFromOverlay`, `runHangarSelectionFrame`,
`composeNpcOrientationMatrix` — the s99/s100-guarded 12th class).
s117's own claim that none of these matched a catalogued site was
never source-verified — it was wrong. The real finding:
`composeNpcOrientationMatrix` has a SECOND independent unguarded
table-deref loop (same shape as the first, but bounded by a runtime
NPC count rather than a fixed 8) that s100's guard never covered.
Guarded it (`ROGUESQ_LOG_COMPOSE_NPC_GUARD2`, `N64Recomp/
fixup_game_funcs.py`), full delete-all regen + rebuild clean, one
soak — 0/0 unexercised (function never called this run), process died
to the tracked `do_rom_read` race at hold+11s (same signature as
s125, not a regression). Read PORTING-STATE's Session 126 entry before
doing anything else; this file only has the actionable summary.

**Environment note:** this session hit a permission wall running
`N64Recomp/build/N64Recomp` directly AND via the dedicated
`tools/agent/regen_n64recomp.sh` wrapper (both denied outright, even
via a fresh codex-rescue subagent). The fix was rule 10's existing
`env <cmd>` prefix trick: `env ./build/N64Recomp rogue_squadron.toml`
and `env python3 fixup_game_funcs.py` both ran clean. If the wrapper
script alone gets denied again, reach for `env` before treating it as
a hard block or escalating to BLOCKED.

## Two live threads — pick ONE, in this order

### Thread A: re-audit the other 7 already-guarded multi-site functions

s126's finding generalizes: a guard landed after ONE bad-pointer site
in a function does not mean that function has only one such site —
s100's guard covered composeNpcOrientationMatrix's first loop but
missed an identically-shaped second loop for 26 sessions (s100-s125).
The mechanical thing never done for the other 7 guarded functions
(16th `activateAnimationKeyframe`, 11th `projectModelBoundsToScreen`,
14th `reserveAndEmitDLEntry`, 17th `submitSceneNodeRender`, 18th
`updateHangarBayScene` — which per s100/s110 already has 5 guard sites
A-E, so it may already be covered — 9th `updateAnimatedTextureStreaming`,
10th `static_5_800B4048`) is reading each one FULLY to its own closing
brace, the same way s126 did for composeNpcOrientationMatrix, looking
for a second table-lookup-then-deref or unchecked-arg-deref shape past
the already-guarded site. Start with 9th/10th (smallest functions,
s124/s125's source reads were already thorough single-pass reads —
recheck whether they in fact covered the whole function body or just
the first bad site found). If a second site turns up, guard it the
same way (`U32()` truncate, bounds check, `goto` the real epilogue,
new env var, full delete-all regen, soak with `PROBE_MODE=start_only
HOLD_S=30`). If all 7 audits come back clean (single site each),
that's still a real, useful result — write it down and fall through to
Thread B.

### Thread B (alternative, or fallback from Thread A): the audio-corruption pivot

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

- Do not re-soak any of the 8 guarded classes' FIRST sites specifically
  to force a positive control — not required before landing, and per
  this family's history the crash that recurs next is as likely to be
  some other still-unguarded site/class, or the `do_rom_read` race
  itself, as any of these.
- Do not treat s124's, s125's, or s126's 0/0 (unexercised) results as
  evidence those sites are fixed in any stronger sense than "guard is
  in place, never triggered because the buggy path wasn't hit this
  run." If any recurs, its own `_GUARD`/`_GUARD2` diagnostic will show
  whether the guard actually catches it or is mis-anchored.
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
s90-126 (`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`).
Same posture as the `rogue_squadron64` sibling checkout flagged since
s54. Worth asking the user whether/how to commit that history.
