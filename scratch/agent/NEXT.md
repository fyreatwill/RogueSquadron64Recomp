# NEXT work unit

HYPOTHESIS-ID: item-320-loadcutscene-sourcetrace

## s564 recap (read this first)

**Item -345 FULLY CLOSED 2/2** (confirm: hangarbay n=2700, 0 attr-write fires, crash on
catalogued coalesceFreeHeapBlocks noise).

**Freelist WRITE residual re-scan after -345: EMPTY.**
- Tracer: 448 reloads, NEEDS_GUARD=21 (was 22 at s562).
- All 21 shape-checked: packing DEFERRED (write-base = DL cursor; freelist reload branch-only).
- Freelist-shaped NEEDS_GUARD = 0. **Freelist WRITE campaign formally CLOSED.**
- Summary: `scratch/agent/s564_residual_summary.json`

**Item -320 escalated:** SOAK-RESULTS recount shows ≥4 independent hangarbay-controlled hits
on exact guest PC `0x800aafb8` (s532 n=31, s536 n=2600, s543 n=31, s563 n=2600) plus s508 filing.
Ledger had undercounted as "2 occ". Distinct from `0x800ab068`/`initVec4TripletFromArgs+68`.

## This iteration's work unit

**Source-trace item -320** (`loadCutsceneAssetsByIndex+1860` / `last-guest-pc=0x800aafb8`).

### Hypotheses
1. **H1:** unguarded freelist/heap pointer deref at/near `0x800AAFB8` (same class as closed
   freelist WRITE campaign — residual gap outside funcs_3/4 tracer scope; function is in
   `funcs_28.c`).
2. **H2:** wild argument / never-initialized slot (like item -261 audio-slot family) — skip-on-
   invalid at function entry or call site is the fix.
3. **H3:** host-side misattribution / shared epilogue (like item -321 REFUTED) — guest PC is
   a delay-slot or shared tail, not a real multi-site corroboration.
4. **H4:** corruption wave already partially caught by other guards; this site is a downstream
   sink needing a local range check on the faulting base register.

### Discriminating measurement
1. Locate every `g_rs64_last_guest_pc = 0x800AAFB8u` / `// 0x800AAFB8` in
   `RecompiledFuncs/funcs_28.c` and identify the enclosing `RECOMP_FUNC` + faulting MEM_* /
   call that can SEGV (pc-symbol said loadCutsceneAssetsByIndex+1860 — verify, don't trust
   offset alone; s541 pc-symbol instability gotcha).
2. For each candidate site: prove which register is the base, where it is loaded, whether a
   range check already exists on any path, and whether skip-on-invalid is safe.
3. If a real unguarded deref: land one fixup guard family (or extend an existing one), one
   build, one live-verify with hangarbay double-digit+ control. If H3 (shared tail): document
   REFUTED with site evidence and do not guard.

### Exact commands
```bash
# Locate sites
grep -n '0x800AAFB8\|0x800aafb8\|loadCutsceneAssetsByIndex' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_28.c | head -40

# Read ±40 lines around each hit; identify enclosing RECOMP_FUNC
# If guard needed: add fixup block + surgical RecompiledFuncs edit, then:
#   DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
# Live-verify with full passive breadcrumb env set (see s563 confirm script as template)
```

### Do NOT
- Re-open freelist WRITE packing DEFERRED sites as freelist-class (s564 closed).
- Re-open -341..-345 / freelist-walk residual (all FULLY CLOSED 2/2).
- Escalate -332 or other 2-occ breadcrumbs until a 3rd independent hit (unless this session's
  soaks produce one — then fold and re-prioritize).
- Source-trace on weak hangarbay n<10 deaths.

## Iron-rule reminders
- Confirm free session number at START (next is s565).
- Weak early deaths on item -306 `setByteAcrossEntryList+176`/`0x800aafa8` with hangarbay n<10:
  discard+retry.
- Never trust 0-fires without double-digit+ hangarbay-entry.
- Kill with SIGKILL; run from build/ with ROM.
- Full guard table: docs/PROJECT-OVERVIEW.md §22-§26.
