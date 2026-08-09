# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s558 recap (read this first)

**Folded in s557's queued confirm — CLEAN, FULLY CLOSED 2/2.**
`s557_residual_count3_seven_way_confirm` (guards 125-131 + item -340 watch):
CLEAN hangarbay n=3000, full ~300s rc=0, 0 fires on all 7 residual tags, 0 sibling-ptr-write
fires, NO crash. **Guards 125-131 FULLY CLOSED 2/2. Item -340 FULLY CLOSED 2/2.**

**Campaign freelist WRITE idioms CLOSED at 131/131 FULLY CLOSED 2/2.**
- Classic r2/0X4: 115/115
- Residual free-list-node rN/0X0 batch 1 (116-124): 9/9
- Residual free-list-node batch 2 (125-131): 7/7

**Fresh residual re-scan after close:** 22 NEEDS_GUARD remaining — ALL packing flow-merge false
positives (DL write-cursor base; freelist reload branch-only) or one freelist-walk *read*.
**Freelist-node write MATCH residual: EMPTY.** Packing formally DEFERRED (not freelist-write scope).

## This iteration's work unit

**Pivot: freelist-walk GUARD4 systematic audit (item -339 shape).**

Item -339 (`emitAllocatedDLCommand`/`0x800088ec`) is still single-occurrence, but freelist-node
write residual is empty so the next M3 class is freelist-walk second-deref after GUARD3 validates
the previous node — same gap heapWalker s218 closed as GUARD4.

### Hypotheses
1. **H1 (gap class real):** emitAllocatedDLCommand GUARD3 covers loop-back on the *old* node but
   leaves the freshly-loaded next pointer unguarded before a second deref — family-wide across
   freelist walks that share the s133 GUARD3 shape.
2. **H2 (site-local):** only the item -339 site (or a tiny handful) lacks GUARD4; most walks are
   already covered by heapWalker GUARD4 / emit_dl GUARD3 / scene-node GUARD3 families.
3. **H3 (not freelist walk):** 0x800088ec is a different idiom misread as GUARD4; source will not
   match `rN = *rN` after GUARD3.
4. **H4 (already covered, log noise):** an existing guard should have caught it but env was off
   or the site is outside the regex.

### Discriminating measurement
1. Source-read `emitAllocatedDLCommand` around guest PC `0x800088ec` and the nearest
   `EMIT_DL_GUARD3` / free-list-walk guard. Map exact instructions: which register is validated,
   which is dereferenced next.
2. Grep-enumerate freelist-walk second-deref sites (same shape as heapWalker GUARD4 / item -339)
   across `funcs_3.c`/`funcs_4.c` that already have GUARD3 but lack a post-load range check.
3. Classify every site: already guarded / needs GUARD4 / shape mismatch / dead.
4. If a non-empty NEEDS_GUARD4 set exists with byte-identical shape: fix as a family (batch
   instrument, one live-verify, queue confirm). If empty after classify: close the pivot and
   pick packing DL-cursor or multi-occurrence breadcrumbs.

### Exact commands (start here)
```bash
# Confirm session number
git log --oneline -3

# Item -339 site context
rg -n '0x800088[Ee][Cc]|EMIT_DL_GUARD3|emit_dl_guard3|emitAllocatedDLCommand' \
  /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py | head -40
# Guest PC window in generated source
rg -n '0x800088[Ee][Cc]|0x800088' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c | head -30
# Existing GUARD4 templates
rg -n 'GUARD4|heapwalker_guard4|unguarded peek-load' \
  /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py | head -40
```

Do NOT re-open freelist-node rN/0X0 or classic r2/0X4 — both residual-empty and FULLY CLOSED.

## Iron-rule reminders
- Confirm free session number at START before naming.
- Guard firing with `n=0` is not automatically dismissible — check bad_ptr vs crash fault address.
- Never trust 0-fires without double-digit+ `hangarbay-entry`.
- One build/run carries every armed guard env var.
- Kill with SIGKILL; run from `build/` with ROM.
- Build that matters: `RogueSquadron64Recomp/build`, not `N64Recomp/build`.
- Full guard table: `docs/PROJECT-OVERVIEW.md` §22-§25.
