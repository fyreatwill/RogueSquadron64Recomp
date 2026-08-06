# NEXT work unit

## s395 recap

Closed the `funcs_27.c` leg of s394's sweep-remainder plan (Step 1). Delegated a full per-site
classification of all 102 raw `-0x25A4` loads to a subagent (two hand-rolled mechanical scripts proved
unreliable first — a proximity-window bug and a regex-lookahead-backtracking bug, both false positives —
so don't repeat that; delegate the actual per-site read from the start). Result: 86 already covered, 15
confirmed SAFE (call-arg-only), 1 genuine NEEDS-GUARD site (`S395_SWEEP_1`) — plus a bonus finding,
independently re-verified by direct source read: the existing `S285_H1_8` guard (s285, chunk 1) checks a
STALE `ctx->r4` left over from an unrelated combine 65 lines earlier, not the fresh value this site
actually needs guarded — the SAME bug class s394 fixed for chunk 3a (item -243/-244), just in a different
session's chunk, never caught because `ROGUESQ_LOG_S285_GUARD` was never armed with a positive control.

Fix: added ONE new guard (`S395_SWEEP_1`, `fixup_game_funcs.py`, bail `S285_H1_BAIL`) anchored correctly
after the real combine, before the dereference. Left the old broken `S285_H1_8` untouched (harmless
dead-weight, a separate deferred cleanup). Verified: regen diff shows ONLY `funcs_27.c`, 14 lines added / 0
removed. Build clean. 4 soaks (more than the usual 3 — two hit pre-existing unrelated log-storm/crash
pathologies that needed working around): verify1 (armed, default env) — scene reached, 574
`[hangar-loop]` positive control, 0 crashes, `[s395-sweep-guard]` fired 0 times (plausible null). verify2
hit a pre-existing `RS_FREE_WALK` log-volume footgun (10GB, already flagged by s345's own comment).
verify2b hit a DIFFERENT pre-existing pathology — a `[mesgqueue-guard]` tight retry loop against a
permanently-bad `mq_=0x1D0` pointer (7GB, `bad_total` reached ~38M) — a NEW observation, not previously
documented. verify2c/verify3 (leaner env avoiding both storms) stayed crash-free but never advanced past
the title screen (VI=1024) within their 280s+ holds — disabling `ROGUESQ_LOG_SCHED` likely desynced the
fixed-time key schedule from actual game timing, so `hangarInitialize` was never entered either run.
verify4 (default env retry) hit an unrelated early-boot crash in `musyxSynthFrame`
(`last-guest-pc=0x8000834c`), well outside `hangarInitialize`'s range. Net: 0 crashes attributable to the
fix across all 4 attempts; verify1 is the fully valid primary evidence. Full detail: `PORTING-STATE`
Session 395; `docs/CURRENT-TRUTH.md` item -245.

## This iteration's work unit: finish the sweep — `funcs_40.c` and `funcs_19.c`

s394's original 3-file plan is now 1/3 done. Two files remain:

### Step 1 — `funcs_40.c` (the `updateHangarBayScene`/`static_5_800A9270` family)

69 raw `-0x25A4` hits vs 67 existing guard/`HANGARLIST_GUARD`/`S284_*`/`S285_A9270_R4`/`G1`-`G32` markers
(see `fixup_game_funcs.py` around line 5225+ for the existing G1-G32 site list). Use the SAME
methodology validated this session: don't hand-roll a mechanical coverage-checker script beyond a rough
raw-count sanity check — delegate the actual per-site classification (existing-coverage check +
NEEDS-GUARD/SAFE/UNCLEAR call) to a subagent, giving it the exact guard-block shape, the s394
anchor-placement lesson (anchor starts AFTER the raw load/combine, never at the raw load's own lines —
this has now bitten TWO different sessions' chunks), and instructions to actually `sed`-read source around
each candidate rather than trust grep proximity alone. This file's guard families are numerous (unlike
funcs_27.c's single big function) — the subagent should also identify the enclosing function name for
each candidate, since bail-label reuse needs a label that's live within THAT function, not borrowed from
a different one.

### Step 2 — `funcs_19.c`'s 1 outlier

Single raw hit, loads directly into `ctx->f28.u32l` (a float register) rather than the
`$sN`-base-pointer-then-ADD32-combine idiom this whole audit targets. Check whether it's actually part of
the same hangar-list-pointer family (unlikely, given the float destination) or an unrelated `-0x25A4`
displacement that happens to coincide — check the enclosing function's identity/purpose before deciding
scope. This is small enough to just read directly, no need to delegate.

### Step 3 — apply guards + verify

Same protocol as every prior chunk (now including s395's own extra lesson): `shutil.copytree` backup,
delete all `funcs_*.c`, regen (`make_elf.py` → `N64Recomp` → `fixup_game_funcs.py`), diff (expect ONLY
`funcs_40.c`/`funcs_19.c` to change, by an amount matching new ADDITIONS), build clean, soak. For the
soak(s): use the DEFAULT `run_s327waitpump.sh` env (do NOT disable `ROGUESQ_LOG_SCHED` or similar
per-tick diagnostics purely to dodge a log-volume issue — s395 found that doing so desyncs the fixed-time
title-screen key schedule and prevents the target scene from ever being reached, which is worse than a
large log). If `RS_FREE_WALK`/`RS_MALLOC_WALK` volume becomes a problem, disable ONLY those two (they are
independently flagged as a known footgun, unlike `ROGUESQ_LOG_SCHED`) — keep `ROGUESQ_LOG_SCHED` and
everything else at its default. Poll `run.log`/the task's own output file directly at intervals (not raw
`sleep`, use short individual waits) rather than relying on notification-only waiting, per s394's own
process lesson (still valid, reconfirmed this session).

## Two bonus observations from s395 (not this iteration's work unit, but worth a look if a slot opens)

1. `S285_H1_8` (funcs_27.c, ~line 122483) is a leftover stale-register guard, checking a value that's no
   longer the one at risk now that `S395_SWEEP_1` covers the real dereference. Harmless but should
   eventually be removed/relocated — a small, low-risk cleanup for whenever the current audit chunk work
   is between files.
2. `[mesgqueue-guard]` (a pre-existing diagnostic, unrelated to this audit) fires in an extremely tight
   loop against a permanently-bad `mq_=0x1D0` pointer, observed reaching a `bad_total` counter of ~38
   million within a single soak's hold window without ever succeeding or giving up. VI/scheduler kept
   progressing normally throughout (not a hang), but this looks like a genuine low-severity bug in the
   message-queue subsystem's own retry logic — worth a dedicated look in a future session, independent of
   the `-0x25A4` idiom-class audit.

## Iteration budget

HYPOTHESIS-ID: m3-idiom-audit-fresh (unchanged — s389, s390, s392, s393, s394, s395 are all under it, this
makes iteration 8; if loop.sh's rule-8 counter forces a pivot preamble, note that s395's find-and-fix of a
SECOND independent stale-guard bug instance is itself a genuinely new, non-repeat contribution to the same
audit thread, matching the same reasoning s393/s394/s395 have each used in turn).
