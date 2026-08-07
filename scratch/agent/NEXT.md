# NEXT work unit

HYPOTHESIS-ID: post-m4-249-closure-awaiting-direction

## s421 recap

Picked up mid-flight from a background subagent (see PORTING-STATE session 421 for the full
delegation-reliability note) that had gotten through: fresh regen (58 actionable candidates — the
item's entire remaining pool, taken as one batch per s420's own handoff plan since it was <=75), probe,
apply, initial full-batch live-verify (**crashed**, `last-guest-pc=0x800290d4`), and a revert positive
control (confirmed the batch, not environment, was responsible) — but the subagent's own turn ended
mid-bisection with only a stale progress note as its final message, not the structured report it was
asked for.

Resumed the halves bisection in-band from that exact point, with full sibling-independence discipline
(every deferred sibling at every split independently live-verified, never inferred clean by
elimination):

    58 -> halfA(29, CLEAN) / halfB(29, CRASH)
           halfB -> B1(15, CRASH) / B2(14, CLEAN, tested independently)
                    B1 -> B1a(8, CLEAN) / B1b(7, CRASH)
                          B1b -> B1b_x(4, CRASH) / B1b_y(3, CLEAN, tested independently)
                                 B1b_x -> p(2, CRASH) / q(2, CLEAN, tested independently)
                                          p -> plotRadarBlipColumn (CRASH ALONE)
                                               plotRadarBlipRow (CLEAN, tested independently)

Six independent branches confirmed clean along the way (halfA, B2, B1a, B1b_y, q, plotRadarBlipRow) —
exactly ONE bad function found, `plotRadarBlipColumn` (`0x800C41B0`), recorded in `m4_known_bad.txt`
with the full narrative. It is the **SIXTH** independent trigger of the `last-guest-pc=0x800290d4`
crash site (after `allocObjectPoolNode`, `tickCraftMountedAnimationEffect`, `stepObjectOrientationTowardTarget`,
`updateHudHealthIndicator`, `buildFormatMessageGlyphBuffer`) — crossing the "pause and source-read"
threshold NEXT.md had flagged since s419, noted here rather than acted on mid-session since it fell out
at the very end of closing the item.

Applied the final 57-name batch (58 minus the one bad function): 8 to `cinematic_overlay.txt`, 49 to
`mission_overlay.txt`. Live-verified clean 2/2 (88.6s/88.5s to phase, 20 frames both runs, 0 `[CRASH]`
markers, 0 `[missing-func]` lines).

**A fresh regen after landing the batch found 0 actionable candidates remaining** — all 14 names still
in `main_overlay.txt` are exactly the union of `m4_known_bad.txt` (10) and `m4_known_skip.txt` (4).
**M4 item -249 is CLOSED**: 784 relocated total (727 + 57 this session), 14 permanently excluded, 798
candidates the family ever surfaced. Full arc migrated to `docs/PROJECT-OVERVIEW.md` §15.

## Why this session ends BLOCKED, not with a queued next work unit

The USER DIRECTIVE (2026-08-04) in `docs/CURRENT-TRUTH.md` set a strict priority order: (1)
maintenance, (2) M5 audio de-stubbing, (3) M3 idiom-class audits only, with M4 item -249 as the
sanctioned fallback once M3's idiom-audit method was exhausted (s397). As of this session, **all three
legs are simultaneously closed or exhausted**:

- M5: closed, fully (PROJECT-OVERVIEW §10-§12).
- M3 idiom-audit-only: exhausted since s397 (codebase-wide frequency scan found no next comparable
  class); the directive already said this needs human reconfirmation to leave idiom-audit-only mode.
- M4 item -249 (the sanctioned fallback used s400-s421): **closed this session.**

There is no longer a sanctioned autonomous work unit under the current directive. Continuing to pick
work unilaterally here would mean either re-opening a track the user explicitly gated behind human
confirmation, or inventing a new direction the directive doesn't cover — both against the spirit of the
USER DIRECTIVE section. Per the loop contract, this is exactly what BLOCKED is for.

## Candidate next work (for the human to confirm/pick from, not to act on unilaterally)

1. **`0x800290d4` root-cause session.** Now has SIX independent trigger functions found via M4
   bisection (`allocObjectPoolNode`, `tickCraftMountedAnimationEffect`, `stepObjectOrientationTowardTarget`,
   `updateHudHealthIndicator`, `buildFormatMessageGlyphBuffer`, `plotRadarBlipColumn`), all below
   `overlay_start` (`0x800A5130`) in core `.text`, not inside any of their own bodies — strong
   circumstantial evidence of one or a few shared downstream corruption sinks reachable from many
   different newly-real call sites. A dedicated session disassembling/instrumenting that address with
   one of the trigger functions active could plausibly explain (and maybe fix) several bad-function
   parks at once. This is the strongest concrete lead the M4 item -249 arc surfaced.
2. **Reconfirm or redirect the USER DIRECTIVE.** All three original legs are now closed/exhausted —
   the directive itself needs a fresh priority order (new M3 discovery tooling? crash-driven discovery
   resumption? something else entirely?).
3. **M3 DoD resumption** (`docs/CURRENT-TRUTH.md` Goal stack, M3 definition-of-done: 60s of in-mission
   rendering, craft responds to synthetic input, stability counters 0, phase timeline covers the
   mission) — the milestone itself has been open since s50 and never directly pursued as its own work
   unit; M4/M5 have absorbed most sessions since. Worth a fresh look now that a huge share of
   `main_overlay.txt`'s phantom-function noise is gone.

## Environment/tooling notes (still accurate, reusable for any of the above)

- `nm` needs `env nm ...` prefix (not directly allowlisted).
- `s417_cycle.sh`/`s417_apply_names.py`/`s417_revert.py` (in `scratch/agent/`) are fully generic — one
  full regen→build→phase-gated-live-verify cycle collapses to `zsh scratch/agent/s417_cycle.sh
  <outdir>`, given `symbol_files/*.txt` already reflect the desired state.
- Symbol-file edits live in the SIBLING repo `~/Documents/Tools/rogue_squadron64`, uncommitted per
  `docs/CURRENT-TRUTH.md` item -3 (do NOT commit there without asking the user first).
- `RecompiledFuncs/funcs_*.c` live at `~/Documents/Tools/N64Recomp/RecompiledFuncs/` (50 files);
  `s417_cycle.sh` deletes and regenerates them automatically before every build.
- Live-verify commands take longer than 120s (phase-width gate alone ~88-89s, plus build) and
  auto-background — use `TaskOutput` with `block=true` to wait synchronously.

## Soak queue

None currently queued.
