# NEXT work unit

HYPOTHESIS-ID: item-299-63fc-dl-buffer-pool-guard

## s465 found+classified a new M3 idiom-class candidate: item -299, global `0x801163FC`, 84 sites
in `funcs_3.c`/`funcs_4.c` (`allocateDisplayListBuffer`/`emitAllocatedDLCommand` and siblings). NOT
YET FIXED — full derivation in `docs/CURRENT-TRUTH.md` item -299. This is the top work unit.

Method used to find it (Option A from the prior NEXT.md, re-run this session): a from-scratch
frequency scan across all 50 `RecompiledFuncs/funcs_*.c` for the shared `lui $reg,0x80XX` immediately
followed by `lw $reg,OFFSET($reg)` idiom (any offset, not just the previously-known ones), bucketed
by `(hi16, offset)`, cross-checked against every offset actually appearing anywhere in
`fixup_game_funcs.py` (not just the obvious `_GUARD` name list — this caught a case-sensitivity bug
in the exclude-list normalizer that would have false-positived `0x63B0`/`0x29C0` as "new"). Scripts:
`~/Documents/Tools/N64Recomp/scratch_s465_scan.py` (the frequency scan) and
`scratch_s465_classify_63fc.py` (the shape classifier for the winning bucket), both untracked, same
convention as `scratch_s454_scan.py`/`scratch_s463_classify_5824.py` before them.

## The idiom, confirmed by reading 5 sample sites spread across the 84-site population

```
ctx->rL = MEM_W(ctx->rL, 0X63FC);            // reload global 0x801163FC (unvalidated)
ctx->rD = MEM_W(ctx->rL, 0X0);               // deref #1: read global->field0 -- CRASH RISK if rL wild
if (ctx->rD != 0) goto Lalready;             // already initialized -> skip to Lalready
    // (delay-slot instruction here varies per site, e.g. `ctx->r4 = ADD32(ctx->r3, 0);` --
    //  NOT confirmed byte-identical across all 84 sites, only sampled at 5)
MEM_W(0X0, ctx->rL) = ctx->rNew;             // deref #2 (WRITE): global->field0 = rNew -- CRASH RISK
goto Ldone;
Lalready:
    ...
Ldone:
    ...
```
Both derefs use `ctx->rL` (the raw, unvalidated reload) as a base address. Same structural risk as
the closed `DL_LIST_APPEND_GUARD`/`DL_LIST_RESET_GUARD` family (item -291/-298) — global
`0x801163FC` sits 76 bytes past `0x801163B0` (`GENERIC_CACHE_GUARD`'s own free-list-cache-head
global), consistent with being a sibling field/list-head in the same struct region, same
`funcs_3.c`/`funcs_4.c` display-list-emission code that has produced every real finding in this
whole lineage.

## This iteration's work unit: finish the shape audit, then patch

### Step 1 (required before patching): confirm the delay-slot instruction and label structure really
is byte-identical (or regex-tolerable) across all 84 sites, not just the 5 sampled

Extend `scratch_s465_classify_63fc.py` (or write a fresh companion script) to dump the FULL block
(reload through the eventual write, both branch targets) for every one of the 84 `DIRECT_WRITE+DEREF_READ`
sites, normalize register numbers/addresses/labels to placeholders, and diff the normalized shapes
against each other. If all 84 normalize to one shape (delay-slot instruction as a captured wildcard
group, like earlier guards captured `addr3`/`addr4`/etc.), a single blanket regex substitution is
safe (`DL_LIST_APPEND_GUARD`'s own precedent). If they diverge, fall back to grouping by normalized
shape (some sites may need per-site literal-anchor patches instead, `SIBLING_PTR_WRITE_GUARD`'s own
precedent) — do NOT assume byte-identical from 5 samples alone, that was this session's discriminating
gap, not a completed proof.

### Step 2: implement the guard

Remediation design (already reasoned through this session, see item -299 in CURRENT-TRUTH): validate
`ctx->rL` immediately after the reload (`0x80000000 <= rL < 0x80800000`, this whole lineage's standard
bound). If invalid: log via a new `[dl-buffer-pool-guard]` tag / `ROGUESQ_LOG_DL_BUFFER_POOL_GUARD` env
var (follow the exact `_enabled`/static-counter/`fprintf` skeleton every prior guard in this file
uses), then **force `ctx->rD` to a nonzero sentinel** (e.g. `1`) so the branch takes the "already
initialized" path and skips BOTH the read-deref's downstream use and the write-deref entirely — do
NOT substitute 0 for `ctx->rD` (that would route into the WRITE branch and still deref the invalid
`ctx->rL` as a write address, the same class of mistake `DL_LIST_RESET_GUARD`'s design notes warn
about avoiding). If valid: execute the original 2 derefs unchanged.

Add the patch to `~/Documents/Tools/N64Recomp/fixup_game_funcs.py` (function-scoped or file-scoped
per the file's own convention, matching `DL_LIST_APPEND_GUARD`'s placement/style), regen per the
mandatory order (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake --build . -j8`),
confirm the patch report shows the expected `x84` (or `x<n1> + x<n2>` if split across shapes) count.

### Step 3: build + live-verify + queue confirm soak

Standard recipe: `env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_DL_BUFFER_POOL_GUARD=1 tools/probe.sh` (or the loop's usual driven-schedule wrapper) from `build/`, phase-gated on VI transitions, full `PROBE_KEYS_FROM_PHASE=1` schedule. Discriminating outcome: 0 `[dl-buffer-pool-guard]` fires expected (matches this whole idiom class's established true-negative baseline, item -287) — a null result is fine as long as `hangarbay-entry` (or equivalent reachability counter) shows the code path was actually reached (positive control, iron rule 1). Then write a confirmation soak recipe to `scratch/agent/soak_queue/s466_dlbufferpool_confirm.sh` (self-contained, same shape as `s464_dllistreset14_confirm.sh`) for the loop to run.

## Fallback if Step 1 finds the shape is NOT uniformly regex-tractable in reasonable time

Park item -299 with the classification findings as-is (already a real, documented result) and fall
back to one of the OTHER buckets found this session, in priority order: `hi16=0x8012,offset=-0x5B48`
(20 sites, `funcs_3.c`/`funcs_4.c` only — same file cluster, smaller population, worth a quick shape
check first since a clean small population may be easier to close outright), then the more scattered
buckets (`0x7CE4`/`-0x70F8`/`-0x5BBC`/`-0x7104`/`-0x35E0`/`0xB50` — all listed with file-spread counts
in CURRENT-TRUTH item -299) if `-0x5B48` also turns out complicated.

## Soak queue status

Both s463 and s464's confirm soaks have now run and been folded into the ledger (see CURRENT-TRUTH
item -298) — nothing outstanding in `scratch/agent/soak_queue/` as of this session end (verify with
`ls scratch/agent/soak_queue/*.sh` — should be empty or only contain non-`.sh` bookkeeping).

## Discriminating instrument still live: watch for `sibling-ptr-write-guard` fires in
`submitSceneNodeRender`

Unchanged from prior sessions — 10 of item -296's 119 sites sit in `submitSceneNodeRender`, tied to
a still-open 2-occurrence wait-for-recurrence breadcrumb. 0 fires across every soak so far including
s465's (this session ran no live soak of its own — pure static analysis/discovery — so this is
carried forward unchanged, not re-confirmed this session).
