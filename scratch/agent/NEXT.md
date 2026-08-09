# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s554 recap (read this first)

**Folded in both of s552/s553's queued confirms that completed — both CLEAN, both FULLY CLOSED 2/2.**
`s552_three_way_tie_confirm` (guards 72-74): CLEAN (`hangarbay-entry n=2700`, 0 fires); crashed on
known BREADCRUMB6 `buildPositionAndCallTransformHelper+1736`/`0x80065acc`.
`s553_count8_count6_thirteen_way_confirm` (guards 75-87): CLEAN (`hangarbay-entry n=2600`, 0 fires);
crashed on known Metal-framework cluster `last-guest-pc=0x800ab0e0`. Guards 1-87 now FULLY CLOSED 2/2
(campaign briefly at 87/87 with zero pending).

**Fresh tracer re-scan: count=7 still shape-mismatched (`0x8000D268`, skipped again); count=3 is a
SINGLE classic site; count=2 is a TWENTY-SIX-WAY TIE (11 NEW functions to this campaign).** Fixed 27
new guards (88-114). 1st live-verify (all 27 armed): clean (`hangarbay-entry n=2600`, 0 fires on all
27); crashed on NEW single-occurrence `beginFrameDLChunk+37740`/`0x8000afa0` filed as item -338. 2nd
confirm queued: `scratch/agent/soak_queue/s554_count3_count2_twentyseven_way_confirm.sh`.

Campaign totals: **114 fixed, 87 FULLY CLOSED 2/2, 27 pending confirm** (88-114).

## This iteration's work unit

**Step 1 — fold in the queued confirm result (do this FIRST).**

1. `s554_count3_count2_twentyseven_way_confirm` (2nd confirm for guards 88-114): expect 0 fires on all
   27 new guard tags (see `scratch/agent/s554_guards_meta.json` or SOAK-RESULTS s554 manual line),
   double-digit+ `hangarbay-entry`. If clean: mark guards 88-114 FULLY CLOSED 2/2.
2. Update `docs/PROJECT-OVERVIEW.md` §25 + `docs/CURRENT-TRUTH.md` item -317. **If any confirm surfaces
   a fire, this is a MAJOR finding — investigate instead of picking a new tier.**
3. If WEAK (no hangarbay / single-digit / item -306 early death): discard and re-queue retry immediately
   (s543–s552 pattern; budget a 3rd attempt).

**Step 2 — re-scan and audit the next-ranked idiom-shape tier (fold-in-then-pick), UNLESS Step 1
surfaced a fire.**

1. Re-run the tracer fresh (no custom `--out`):
   ```
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   python3 scratch/agent/s548_dedupe_shape_filtered.py
   ```
2. Filter to reg=`r2`/off=`0X4`. Skip count=7 `0x8000D268` shape mismatch again.
3. s554 took count=3 (1 classic) + count=2 (26 classic). The next tier is count=1
   (`heapFreeListInsert`/`0x800079D8` was already shape-classic in s554's scan — deferred) plus any
   remaining residual classic singles the shape filter surfaces after the count=2 batch is closed.
4. **Shape-check every candidate** (s553 lesson): classic `lui $v0,0x8011` / `lw $v0,0x63B0($v0)` /
   `beq $v0,$zero` / fallthrough `MEM_W(0X4, ctx->r2)`. Sites where `ctx->r2` comes from `$s0`/`addu`
   are NOT this campaign's idiom.
5. Note: some sites store RHS=`ctx->r4` not `ctx->r3` (s554 `allocateDisplayListBuffer` precedent) —
   preserve the exact store operand in the patch.
6. Cross-check every write's OWN guest address against
   `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
7. Fix with established template; name `<FUNC>_R<N>_GUARD` after checking
   `grep -oE "<FUNC_UPPER>_R[0-9]+_GUARD" fixup_game_funcs.py | sort -u`.
8. Regen (all four steps; delete `funcs_*.c` first via python glob+os.remove):
   ```
   cd /Users/williambuckley/Documents/Tools/N64Recomp
   python3 -c "import glob, os; [os.remove(f) for f in glob.glob('RecompiledFuncs/funcs_*.c')]"
   cd /Users/williambuckley/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py
   cd /Users/williambuckley/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml
   python3 fixup_game_funcs.py > <path inside RogueSquadron64Recomp>/scratch/agent/sNNN_fixup_report.txt
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build && \
     DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8
   ```
9. 1st live-verify: copy `scratch/agent/soak_queue/s554_count3_count2_twentyseven_way_confirm.sh`
   (or the done/ manual), append new `ROGUESQ_LOG_*=1`, point `--out` at a new results dir.
10. If `hangarbay-entry` is single-digit or absent, discard and retry immediately.
11. If clean: queue 2nd confirm; record in CURRENT-TRUTH + SOAK-RESULTS + PORTING-STATE.

**Discriminating outcome**: 0 fires across 1st verify + 2nd confirm with real `hangarbay-entry`
promotes guards to FULLY CLOSED 2/2. A nonzero fire whose `bad_ptr` traces to a crash fault address
(item -334 precedent) is a confirmed real bug catch. When the classic r2/0X4 shape filter returns
empty (or only residual non-classic), the step-3 r2/0X4 campaign is done — pivot to residual
idiom shapes (r4/0X0 mesh sites, or the scoped `DL_LIST_APPEND_DEREF_GUARD`-style readback gap audit
flagged s549+).

## Iron-rule reminders specific to this campaign
- Confirm free session number at START (`git log --oneline -3`) before naming.
- Guard firing with `n=0` is not automatically dismissible — check bad_ptr vs crash fault address
  (s549 item -334).
- Never trust tracer tier count without shape check + address cross-check + source read.
- Never trust 0-fires without double-digit+ `hangarbay-entry`. Absent hangarbay = discard immediately.
- Two consecutive weak draws on the same target is now the norm for the item -306 signature (s548–s552);
  budget a 3rd attempt (s553 closed 64-65 on attempt 3 with n=2600).
- Count=N tiers can include shape-mismatched sites that share a taint count but not the classic reload
  (s553/s554 count=7 `0x8000D268` skipped).
- One build/run carries every armed guard env var.
- `s506_dedupe.py` fixed path; never pass custom `--out` to `--scan`.
- Kill with SIGKILL; capture paths must not start with "."; run from `build/` with ROM.
- `fixup_game_funcs.py` is untracked in the standalone N64Recomp checkout — nothing to commit there.
- Build that matters: `RogueSquadron64Recomp/build`, not `N64Recomp/build`.
- `0x800ab068` / `0x80015544` / `findLookupEntryByKey+2212` / `0x80010b7c` pc-symbol instability:
  cross-check `last-guest-pc` only.
- item -332 watch (2 occurrences); item -331/-333 free-list-pop region watch; item -335/-336/-337/-338
  single-occurrence watch.
- After launching manual live-verify in background, wait with TaskOutput block timeout ≥300000ms.
- Full guard table: `docs/PROJECT-OVERVIEW.md` §22-§25.
