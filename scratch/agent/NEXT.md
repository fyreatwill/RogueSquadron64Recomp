# NEXT work unit

HYPOTHESIS-ID: breadcrumb-triage-post-symbolizer-fix

## s480 summary: crash-symbolizer tooling fix implemented and positive-control validated (item -311,
DONE)

Closed the s478-flagged tooling candidate: `src/main/main.cpp`'s crash handler now resolves the
faulting ARM64 host PC against a self-built local+exported symbol table (`nm -n` on the running
binary, parsed once at startup, binary-searched from the signal handler with zero allocation) before
falling back to `dladdr`. Scope check confirmed no dSYM exists and `nm -n` already prints real names
for internal-linkage symbols, so the cheap H1 design (not dSYM/`atos`) was correct. Validated with a
deliberate crash inside `do_lwl` (one of the actual functions in item -310's 40KB gap): correctly
symbolized as `do_lwl+60 (local-symtab)`, not misattributed. Reverted the temporary test trigger
(`lib/N64ModernRuntime/N64Recomp/include/recomp.h`), confirmed `git diff --stat -- lib/
N64ModernRuntime` shows 0 net change (no `export.sh` run needed), rebuilt clean, ran a ~20s untouched
soak: symtab loads (66526 symbols), 0 `[CRASH]`, normal steady-state traffic. Full derivation:
`PORTING-STATE.md` Session 480; ledger entry: `docs/CURRENT-TRUTH.md` item -311.

**Practical effect for future sessions:** any `[CRASH][pc-symbol]` line now says `(local-symtab)` or
`(dladdr-fallback)`. A future `heapFreeListDequeue`-attributed crash is genuinely that function now
(the old blind spot is closed) — do not apply item -310's "probably a misattribution" discount to
any crash log from s480 onward.

## This session's top work unit: read `scratch/agent/SOAK-RESULTS.md` fresh, act on what's there

Nothing was queued as of s479; check the tail again at session start (read list #3) — the loop may
have run new queued soaks between s479 and this session. If something new landed, fold it into the
ledger like any other run evidence before choosing further work.

## Fallback order (per USER DIRECTIVE, unchanged)

1. **Lower-recurrence breadcrumb triage**: `loadCutsceneAssetsByIndex+1860` (2 hits so far, s463/
   s468, both filed-not-chased) is the next candidate if nothing new is in SOAK-RESULTS.md. With the
   symbolizer fix in place, a fresh occurrence's `pc-symbol` line is now trustworthy — worth actually
   pursuing this one now rather than filing a 3rd hit, since two independent confirmations plus a
   reliable symbolizer is a legitimate discriminating-evidence bar per iron rule 4.
2. A new M5 lead (checked clean as recently as s478 — check again only if #1 yields nothing).
3. If neither yields a concrete, boundable unit: BLOCKED with a specific question — M3's two
   opcode-scan lineages, its highest-recurrence breadcrumb, and M5 are all closed/clean, and the
   symbolizer tooling gap is now closed too; ask the human what should replace them as the standing
   M3 discovery method.

## Soak queue status

None queued this session (this was a targeted code-change unit with its own inline validation, not
a soak-queue candidate — the positive-control test used a temporary, reverted crash trigger, so
there's nothing safe to leave queued). Raw positive-control log: `scratch/agent/soak_results/
s480_symtab_positive_control.log`. Check `scratch/agent/SOAK-RESULTS.md` tail at the start of next
session as usual.
