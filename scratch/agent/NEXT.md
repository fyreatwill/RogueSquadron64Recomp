# NEXT work unit

HYPOTHESIS-ID: m3-opcode-scan-lineage-closed

## s477 summary: `lui`+`sw` direct-store scan CLASSIFIED AND DEFERRED, dead end after one scan

Wrote `scratch_s477_sw_scan.py` (N64Recomp repo, untracked) per the s476 pivot note, scanning for
`lui` immediately followed by a direct store (`MEM_W(OFFSET, ctx->rL) = ...;`) off the same
register with NO intervening `lw` reload — the mirror-image of the exhausted read-side (`lui`+`lw`)
lineage. Result: 546 buckets, 1471 sites, 358 singleton buckets (long diffuse tail). Top 3 buckets
(230/197/85 sites) are ALL offsets already well-understood from the read-side lineage (items
-296/-305/-306); direct-read confirmed all three are plain `someGlobal = value;` assignments — the
store destination is a fixed compile-time RDRAM address, which cannot fault regardless of the
register's prior contents. Confirms hypothesis 1 (top clusters = benign fixed-address stores) and
hypothesis 3 (diffuse tail) from the prior NEXT.md; hypothesis 2 (write through a dynamically
reloaded pointer) is structurally excluded by this scan's own match shape. No code change, no soak
queued. Filed as item -309 in `docs/CURRENT-TRUTH.md`.

**Both `lui`-based opcode-pattern scan angles this lineage has tried are now closed**: read-side
(`lui`+`lw`, s454-s476) and write-side (`lui`+`sw` direct store, s477). No untried
high-expected-value instruction-pattern scan is queued. Full derivation: `PORTING-STATE.md` Session
477; ledger: `docs/CURRENT-TRUTH.md` item -309.

## This session's top work unit: no new opcode-pattern scan — fall back per USER DIRECTIVE order

Per the USER DIRECTIVE (`docs/CURRENT-TRUTH.md` top) and this session's finding, M3 idiom-class
scanning has no queued high-value candidate right now. Do NOT invent a third opcode-pattern scan
speculatively — that would be the same mistake NEXT.md has warned against every session ("if you
find yourself re-deriving from the same table, stop"). Options, in priority order:

1. **Check for a new M5 lead first** (priority 2 in the USER DIRECTIVE, above M3). M5 audio
   de-stubbing is marked DONE/fully CLOSED in the directive with "next M5 work needs a genuinely new
   lead" — read `docs/PROJECT-OVERVIEW.md` §10-§12 (the full M5 arc) to check whether any of the
   crash breadcrumbs collected in recent soaks (see SOAK-RESULTS.md tail) plausibly point to a new
   audio-related lead that would justify reopening M5. If nothing new surfaces in a focused ~15
   minute read, treat M5 as still closed and move to option 2.
2. **Passive breadcrumb triage**: `scratch/agent/SOAK-RESULTS.md` and recent session crash
   signatures (search PORTING-STATE.md sessions s449-s477 for "filed, not chased" / "filed not
   chased" crash signatures) have accumulated several NOT-YET-audited crash families surfaced as
   side effects of confirm soaks — e.g. the recurring `near-0x80000000`/"near-zero guest pointer"
   family (BREADCRUMB6, first seen s273), and various `pc-symbol=...+NNNN` one-off signatures. Pick
   the crash signature with the HIGHEST recurrence count across sessions (not the most recent) and
   apply the s282-s288 systematic-idiom-class-audit model to it: is it actually one root cause
   recurring, or several coincidentally-similar symptoms? This is genuinely new work, not a
   re-derivation of the closed lui+lw/lui+sw tables.
3. If neither 1 nor 2 yields a concrete, boundable work unit within the session, the honest move is
   BLOCKED with a specific question for the human: what should M3/M5 priority be now that both
   opcode-scan angles and the standing audio-destub arc are closed. Do not manufacture a
   maintenance-only session to stay busy (ITERATION.md explicitly forbids using doc-housekeeping as
   a way to keep the loop fed).

## Soak queue status

None queued this session (s477 had no code change to verify — the sw-scan and its follow-up reads
were both read-only investigation). Check `scratch/agent/SOAK-RESULTS.md` tail at the start of next
session as usual for any soaks the loop ran in the background.
