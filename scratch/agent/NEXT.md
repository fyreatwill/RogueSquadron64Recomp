# NEXT work unit

HYPOTHESIS-ID: m3-crash-symbolizer-blindspot

## s478 summary: `heapFreeListDequeue+NNNN` crash family INVESTIGATED AND CLOSED — symbolizer artifact, not a real bug

Per the s477 fallback order (M5-lead-check, then passive-breadcrumb triage), an M5-lead check
found nothing new (no code change needed, see `docs/CURRENT-TRUTH.md` USER DIRECTIVE note). Fell
through to passive-breadcrumb triage: ranked all "filed, not chased" recurring crash signatures by
session count and picked the highest, `heapFreeListDequeue+NNNN` (15+ sessions, s108-s477).
Discriminating measurement: direct guest-address arithmetic against `heapFreeListDequeue`'s
confirmed base (`0x8000CFD4`) against the two available `last-guest-pc` data points — neither
matches the implied `+NNNN` guest offset (off by 18-30 KB both times). Root cause: the host crash
handler (`src/main/main.cpp:1788`) symbolizes via `dladdr()`, which only resolves the nearest
EXPORTED symbol; `nm -n` on the built binary shows a 40,648-byte unexported-code gap after
`heapFreeListDequeue` populated by unrelated guard-flag statics from OTHER already-closed guard
families, so any host crash landing anywhere in that gap gets misattributed to
`heapFreeListDequeue+bignum`. **Verdict: not one recurring bug — a symbolizer blind spot.** No
guard written (nothing to guard). Filed as item -310 in `docs/CURRENT-TRUTH.md`; full derivation
`PORTING-STATE.md` Session 478.

**Practical consequence for future sessions**: do NOT re-file future `heapFreeListDequeue+NNNN`
occurrences as "same family, filed not chased" — each is very likely an unrelated crash colliding
with this blind spot, and grouping them under one label is exactly what prevented this from being
investigated for 15+ sessions.

## This session's top work unit

`docs/CURRENT-TRUTH.md` is 63,069 bytes (over the 60,000-byte Step-0 threshold after s478's
addition) — **the next iteration should be a MAINTENANCE iteration per ITERATION.md Step 0**,
regardless of anything below. Do that first; do not skip it because this file suggests other work.

After maintenance, the next real work unit, in priority order (per the standing USER DIRECTIVE —
M5 checked clean s478, M3 opcode-scan lineage closed s476/477, M3 highest-recurrence breadcrumb
closed s478):

1. **The s478-flagged tooling fix: crash-symbolizer blind spot.** `src/main/main.cpp`'s crash
   handler uses `dladdr()` (nearest-EXPORTED-symbol only) to name the faulting host PC. Fix:
   resolve against a finer-grained table instead — either (a) a build-time `nm -n` snapshot of the
   built executable's FULL (including internal-linkage/static) symbol table, loaded and consulted
   by the crash handler at crash time in place of/alongside `dladdr`, or (b) `atos` against a dSYM
   if one is being generated. Discriminating test: force a crash inside a known internal-linkage
   static near `heapFreeListDequeue` (e.g. trip one of the `s_drainmesh*`/`s_coalesceheap*` guard
   asserts deliberately with an env var) and confirm the NEW symbolizer correctly names that
   static instead of misattributing to `heapFreeListDequeue`. This is a real infrastructure
   improvement that will make ALL future crash-signature triage more accurate, not just this one
   family — worth the investment. Scope check before starting: confirm whether the build already
   produces a dSYM (`ls build/*.dSYM` or `dsymutil` in the CMake config) before choosing (a) vs (b).
2. **If (1) turns out to be a bigger lift than one work unit**, fall back to lower-recurrence
   breadcrumb triage: `loadCutsceneAssetsByIndex+1860` (2 hits, s463/s468) or any other signature
   accumulated in `scratch/agent/SOAK-RESULTS.md` since s473 that hasn't been triaged yet — read
   the tail of that file at session start (read list #3) first, since the loop runs soaks between
   iterations and may have surfaced something new.
3. If neither yields a concrete, boundable work unit, BLOCKED with a specific question: M3's two
   opcode-scan lineages, its highest-recurrence breadcrumb, and M5 are all now closed/clean — ask
   the human what should replace them as the standing M3 discovery method.

## Soak queue status

None queued this session (s478 was read-only investigation, no code change to verify). Check
`scratch/agent/SOAK-RESULTS.md` tail at the start of next session as usual.
