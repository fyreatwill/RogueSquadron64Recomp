# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s553 recap (read this first)

**Folded in both of s552's queued confirms that completed — both CLEAN, both now FULLY CLOSED 2/2.**
`s552_emit_allocated_dl_command_r1_reserve_and_emit_dl_entry_r1_confirm_retry2` (guards 64-65, 3rd
attempt after 2 consecutive weak draws): CLEAN full 300s (`hangarbay-entry n=2600`, 0 fires, no crash).
`s552_six_way_tie_confirm_retry` (guards 66-71): CLEAN (`hangarbay-entry n=2600`, 0 fires); crashed on
known background-noise guest PC `0x80010b7c` (this run `loadTextureTile+17912`). Guards 1-71 now FULLY
CLOSED 2/2. `s552_three_way_tie_confirm` (guards 72-74) was still in the queue at end of s553 — fold it
in first if the loop has run it.

**Fresh tracer re-scan: remaining count=8 is a SINGLE classic site; count=7 is a shape mismatch
(skipped); count=6 is a TWELVE-WAY TIE.** Fixed 13 new guards (75-87) including new function
`drawFrameProfilerBars` (R1) and extending `heapFreeListDequeue` to R2/R3 (R2 at `0x8000D6D4` sits near
items -331/-333 free-list-pop region). 1st live-verify (all 13 armed): clean full 300s, `hangarbay-entry
n=3000`, 0 fires, no crash. 2nd confirm queued:
`scratch/agent/soak_queue/s553_count8_count6_thirteen_way_confirm.sh`.

Campaign totals: **87 fixed, 71 FULLY CLOSED 2/2, 16 pending confirm** (72-74 + 75-87).

## This iteration's work unit

**Step 1 — fold in ALL queued confirm results (do this FIRST).**

1. `s552_three_way_tie_confirm` (2nd confirm for guards 72-74): expect 0 fires on
   `heap-free-list-dequeue-r1-guard`, `submit-scene-node-render-r8-guard`,
   `build-oriented-face-geometry-r1-guard`, double-digit+ `hangarbay-entry`. If clean: mark guards
   72-74 FULLY CLOSED 2/2.
2. `s553_count8_count6_thirteen_way_confirm` (2nd confirm for guards 75-87): expect 0 fires on all 13
   new guard tags listed in the s553 SOAK-RESULTS manual line, double-digit+ `hangarbay-entry`. If
   clean: mark guards 75-87 FULLY CLOSED 2/2.
3. Update `docs/PROJECT-OVERVIEW.md` §25 + `docs/CURRENT-TRUTH.md` item -317. **If any confirm surfaces
   a fire, this is a MAJOR finding — investigate instead of picking a new tier.**

**Step 2 — re-scan and audit the next-ranked idiom-shape tier (fold-in-then-pick), UNLESS Step 1
surfaced a fire.**

1. Re-run the tracer fresh (no custom `--out`):
   ```
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   python3 scratch/agent/s548_dedupe_shape_filtered.py
   ```
2. Skip `renderLitTexturedMeshFaces`/`renderFlatMeshFaceGroup` reg=`r4`/off=`0X0` (shape mismatch —
   `ctx->r4` is the function's own non-null `$a0` argument). Filter to reg=`r2`/off=`0X4`.
3. s553 took count=8 (1 classic site) + count=6 (12-way classic). Count=7 was shape-mismatched and
   skipped. The next tier below count=6 is UNKNOWN — find it fresh. Expect many count=2 / count=3
   sites and possibly remaining count=1 singles.
4. **Shape-check every candidate** (s553 lesson): a high taint count is not enough — the write site
   must have the classic `lui $v0,0x8011` / `lw $v0,0x63B0($v0)` / `beq $v0,$zero` / fallthrough
   `MEM_W(0X4, ctx->r2)` idiom. Sites where `ctx->r2` comes from `$s0`/`addu`/other are NOT this
   campaign's idiom even if the tracer tags them.
5. Also worth a scoped look (flagged s549+, not started): does the `DL_LIST_APPEND_DEREF_GUARD` shape
   (checked address, later value READ BACK from guest memory left unguarded) recur in OTHER
   already-"closed" families (`GENERIC_CACHE_GUARD`, `CACHE_HEAD_A1_GUARD`, etc.)?
6. Cross-check every write's OWN guest address against
   `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` (only the write address being
   present is disqualifying; incidental reload-address matches elsewhere are fine — s545).
7. Read generated source around each target; match OLD text exactly (some sites lack
   `g_rs64_last_guest_pc`; some have it — s551/s552/s553).
8. Fix with established template; name `<FUNC>_R<N>_GUARD` after checking
   `grep -oE "<FUNC_UPPER>_R[0-9]+_GUARD" fixup_game_funcs.py | sort -u`.
9. Regen (all four steps; delete `funcs_*.c` first via python glob+os.remove):
   ```
   cd /Users/williambuckley/Documents/Tools/N64Recomp
   python3 -c "import glob, os; [os.remove(f) for f in glob.glob('RecompiledFuncs/funcs_*.c')]"
   cd /Users/williambuckley/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py
   cd /Users/williambuckley/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml
   python3 fixup_game_funcs.py > <path inside RogueSquadron64Recomp>/scratch/agent/sNNN_fixup_report.txt
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build && \
     DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8
   ```
10. 1st live-verify: copy `scratch/agent/soak_queue/s553_count8_count6_thirteen_way_confirm.sh` (or the
    done/ manual), append new `ROGUESQ_LOG_*=1`, point `--out` at a new results dir. Path-prefix
    gotcha: script under `soak_queue/` needs `../../..` to repo root.
11. If `hangarbay-entry` is single-digit or absent, discard and retry immediately (s543–s552).
12. If clean: queue 2nd confirm; record in CURRENT-TRUTH + SOAK-RESULTS + PORTING-STATE.

**Discriminating outcome**: 0 fires across 1st verify + 2nd confirm with real `hangarbay-entry`
promotes guards to FULLY CLOSED 2/2. A nonzero fire whose `bad_ptr` traces to a crash fault address
(item -334 precedent) is a confirmed real bug catch.

## Iron-rule reminders specific to this campaign
- Confirm free session number at START (`git log --oneline -3`) before naming.
- Guard firing with `n=0` is not automatically dismissible — check bad_ptr vs crash fault address
  (s549 item -334).
- Never trust tracer tier count without shape check + address cross-check + source read.
- Never trust 0-fires without double-digit+ `hangarbay-entry`. Absent hangarbay = discard immediately.
- Two consecutive weak draws on the same target is now the norm for the item -306 signature (s548–s552);
  budget a 3rd attempt (s553 closed 64-65 on attempt 3 with n=2600).
- Count=N tiers can include shape-mismatched sites that share a taint count but not the classic reload
  (s553 count=7 `0x8000D268` skipped).
- One build/run carries every armed guard env var.
- `s506_dedupe.py` fixed path; never pass custom `--out` to `--scan`.
- Kill with SIGKILL; capture paths must not start with "."; run from `build/` with ROM.
- `fixup_game_funcs.py` is untracked in the standalone N64Recomp checkout — nothing to commit there.
- Build that matters: `RogueSquadron64Recomp/build`, not `N64Recomp/build`.
- `0x800ab068` / `0x80015544` / `findLookupEntryByKey+2212` / `0x80010b7c` pc-symbol instability:
  cross-check `last-guest-pc` only.
- item -332 watch (2 occurrences); item -331/-333 free-list-pop region watch; item -335/-336/-337
  single-occurrence watch.
- After launching manual live-verify in background, wait with TaskOutput block timeout ≥300000ms.
- Full guard table: `docs/PROJECT-OVERVIEW.md` §22-§25.
