# NEXT work unit

HYPOTHESIS-ID: crash-symbolizer-tooling-fix

## s479 summary: MAINTENANCE iteration — CURRENT-TRUTH.md compacted 713→513 lines (200 net), one
real ordering bug fixed

Step 0 triggered (63,069 bytes > 60,000 threshold). Migrated items -303..-310 (s470-478) full
derivations into `docs/PROJECT-OVERVIEW.md` §19 (new section, following the §16-§18 pattern);
replaced with short range-pointer summaries in CURRENT-TRUTH.md, matching the style already used
for older closed arcs. Found and fixed a genuine numbering-order bug: item -6 was sitting between
items -249 and -239..-247 (wrong magnitude range) instead of between -7 and -5 where it belongs
per the file's own declared "highest-magnitude-negative first" convention — moved it. Also
deleted a fully redundant standalone `-292` entry that duplicated the `-291..-297` range-pointer
paragraph. Net result: 713→513 lines (200 removed, exactly meeting the ADVANCED threshold),
63,069→44,442 bytes. No experiments run this session (maintenance iterations don't run them). Full
writeup: `PORTING-STATE.md` Session 479.

## This session's top work unit: the s478-flagged crash-symbolizer tooling fix

`src/main/main.cpp:1788`'s crash handler symbolizes the ARM64 HOST PC via `dladdr()`, which only
resolves the nearest **exported** symbol. `nm -n` on the built binary shows a 40,648-byte
unexported-code gap after `heapFreeListDequeue` populated by many unrelated internal-linkage
guard-flag statics from other closed guard families — any host crash landing anywhere in that gap
gets misattributed to `heapFreeListDequeue+bignum` regardless of the real faulting function (item
-310, `docs/CURRENT-TRUTH.md`, full derivation `docs/PROJECT-OVERVIEW.md` §19). This is a systemic
symbolization blind spot, not limited to that one function — any internal-linkage function/static
anywhere in the binary is equally mis-attributable to whatever exported symbol happens to precede
it. Fixing it will make every future crash-signature triage session more accurate, not just this
one family.

**Competing hypotheses for the fix's scope/design:**
1. **H1 — a build-time `nm -n` snapshot is sufficient.** Generate a sorted (address, symbol) table
   from `nm -n build/RogueSquadron64Recomp` at build time (or read it lazily at crash time from the
   binary's own symbol table via `dladdr`'s `dli_fbase` + a parsed `nm` dump), and have the crash
   handler do a binary-search nearest-preceding-symbol lookup against BOTH exported and
   internal-linkage (local, `t`/`d` in nm output) symbols instead of relying on `dladdr` alone.
   Cheap, no new build dependency beyond `nm` (already used manually all session).
2. **H2 — a dSYM + `atos` is needed for full accuracy.** If the build doesn't already emit a dSYM,
   internal statics might not even be in `nm`'s output with useful names (could be stripped or
   have compiler-mangled names), and `atos` against a dSYM might resolve to source file:line
   instead of just a symbol name, which is strictly more actionable for future triage.
3. **H3 — neither is needed; the crash handler should just log BOTH the raw host PC offset from
   the binary's own `__TEXT` base AND the nearest guest-side `last-guest-pc` breadcrumb, and defer
   symbol resolution to `atos`/`nm` run OFFLINE by a human/future session against the exact build
   that crashed**, since build addresses shift between builds and a live in-process symbol table
   is more fragile to maintain than a raw offset + offline lookup.

**Discriminating measurement — scope check first, per s478's own note:** before choosing between
H1/H2/H3, run `ls build/*.dSYM 2>&1` and check the CMake config
(`grep -rn "dsymutil\|DEBUG_INFORMATION_FORMAT\|GENERATE_DEBUG" CMakeLists.txt src/CMakeLists.txt
2>/dev/null` or equivalent) to see whether a dSYM is already being produced. If yes → H2 is nearly
free (just wire up `atos` instead of `dladdr`) and is strictly better than H1, pick it. If no →
compare the cost of adding dSYM generation (build-time cost, disk cost, CI/regen-pipeline
interaction) against just parsing `nm -n`'s output once at build time (H1) or logging a raw offset
for offline lookup (H3, near-zero implementation cost but defers the payoff to whoever triages the
next crash).

**Validation, once implemented:** force a deliberate crash inside a KNOWN internal-linkage static
near `heapFreeListDequeue` (e.g. add a temporary env-gated `abort()`/null-deref inside one of the
`s_drainmesh*`/`s_coalesceheap*` guard-flag statics identified in item -310's derivation) and
confirm the NEW symbolizer correctly names that specific static (or its containing function/file:
line) instead of misattributing to `heapFreeListDequeue`. This is the positive control — without
it, "the fix compiles and links" is not evidence it actually resolves anything better than before
(iron rule 1).

**If this turns out to be a bigger lift than one work unit** (e.g. H2's dSYM wiring interacts
badly with the existing regen pipeline, or nm-parsing at crash-signal-time hits async-signal-safety
constraints — `main.cpp`'s crash handler almost certainly runs from a signal handler, so any fix
must avoid `malloc`/`fopen`/etc. inside the handler itself; check this explicitly before writing
code, since it's a real correctness constraint on H1/H2 alike): scope down to just the scope-check
above plus a design writeup in NEXT.md, and defer actual implementation to the following session
rather than rushing a signal-unsafe fix into place.

## Fallback order (unchanged from s478's note, still applies)

1. Lower-recurrence breadcrumb triage: `loadCutsceneAssetsByIndex+1860` (2 hits, s463/s468) or
   anything new accumulated in `scratch/agent/SOAK-RESULTS.md` since s473 — read its tail at
   session start (read list #3) first; nothing new was queued as of s479 (checked, tail unchanged
   since s473's confirm).
2. A new M5 lead (checked clean as recently as s478).
3. If none of the above yields a concrete, boundable unit: BLOCKED with a specific question — M3's
   two opcode-scan lineages, its highest-recurrence breadcrumb, and M5 are all closed/clean; ask
   the human what should replace them as the standing M3 discovery method once the symbolizer fix
   is also done.

## Soak queue status

None queued this session (maintenance iteration, no code change to verify). Check
`scratch/agent/SOAK-RESULTS.md` tail at the start of next session as usual — as of this session it
still ends at `s473_siblingptrwrite120_confirm` (s478 was also read-only, queued nothing).
