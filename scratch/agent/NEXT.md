# NEXT work unit

HYPOTHESIS-ID: dl-list-append-guard-5824

## s454: BLOCKED on a live concurrent process, but real analysis landed

s454 was assigned to open a fresh M3 idiom-class audit (the tracked backlog closed s453). It found
one, designed a fix, but discovered mid-session that `tools/agent/loop.sh` was ALREADY running a
live, independent iteration doing the same thing concurrently (evidence: `scratch/agent/loop.log`
showed "iteration 2 starting" logged at the same moment s453 committed, still running 15+ minutes
later; `ps aux` confirmed a live spawned `claude` process; a scratch file s454 wrote
(`N64Recomp/scratch_s454_scan.py`) was independently rewritten mid-session by that other process;
`N64Recomp/RecompiledFuncs/*.c` went empty then got repopulated by a fixup run that did NOT contain
s454's own patch). s454 correctly withheld regen/build/live-verify/soak/commit-of-code to avoid
corrupting the concurrent process's work on the same shared, non-git-tracked files. Full trail:
`PORTING-STATE.md` Session 454, `docs/CURRENT-TRUTH.md` item -291.

## FIRST STEP, before anything else: confirm exclusivity

```
ps aux | grep -i "loop.sh\|claude-fable" | grep -v grep
tail -80 scratch/agent/loop.log
git -C /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp log -5 --oneline
```
If a `loop.sh`/spawned-`claude` process is still live, or `git log` shows a NEW commit past
`fe67d73` that isn't yours, **stop and reconcile first**: read that commit's message and diff to
see what it actually did before touching anything. It may have (a) done unrelated work and this
session's plan still applies cleanly, (b) found and fixed the SAME `-0x5824` class already (check
`fixup_game_funcs.py` for `DL_LIST_APPEND_GUARD` — if present and it's not yours, don't duplicate,
verify/soak it instead), or (c) found a completely different idiom class (fine, this plan still
applies as a follow-on work unit, just renumber/reconcile the item list).

Only once you've confirmed no other process is live AND reconciled `git log`, proceed.

## The work unit itself (design already done, just needs execution)

`fixup_game_funcs.py` (N64Recomp repo, untracked) already has a `DL_LIST_APPEND_GUARD` patch block
inserted right after `GENERIC_CACHE_GUARD` (search for `DL_LIST_APPEND_GUARD` to find it — if it's
missing, someone reverted/lost it; re-derive from PORTING-STATE Session 454's exact code, or redo
the scan below from scratch). It targets a doubly-linked-list-append idiom at `-0x5824($reg)` →
global `0x8011A7DC`, resolved via `lui $reg, 0x8012`, with NO existing check:
```
ctx->rL = MEM_W(ctx->rL, -0X5824);   // reload global G
ctx->rD = MEM_W(ctx->rL, 0X0);        // deref G unguarded
MEM_W(0X0, ctx->rD) = ctx->rW;         // deref rD (loaded from G) unguarded
ctx->rL = MEM_W(ctx->rL, 0X0);         // reread G->field0
MEM_W(0X4, ctx->rW) = ctx->rL;          // new node->field4 = old field0
```
57/57 sites verified byte-identical in shape (26 funcs_3.c, 31 funcs_4.c — `allocateDisplayListBuffer`,
`emitFrameRdpInitDl`, `emitColorFillRect`, `drawFrameProfilerBars`, `emitMaterialTexturedDLAlt`,
`renderFlatMeshFaceGroup`, `buildOrientedFaceGeometry`, `renderLitMeshFaceGroup`, `drawTextGlyphRect`,
`drawSubtitleText`, `setupCameraMatrices`). Same code area (funcs_3.c/funcs_4.c display-list
emission) as 4 already-fixed sibling crash families protecting a DIFFERENT global
(`0x801163B0`: `GENERIC_CACHE_GUARD`/`CACHE4_GUARD`/`CACHE_HEAD_A1_GUARD`/`FREELIST_NEXT_GUARD`).

### Steps
1. Confirm exclusivity (above).
2. Raw regen if the tree might be stale (check `RecompiledFuncs/funcs_3.c` mtime vs.
   `fixup_game_funcs.py` mtime — if the .c files predate your last edit to the patch, regen):
   `rm N64Recomp/RecompiledFuncs/funcs_*.c` → `cd rogue_squadron64 && python3 tools/make_elf.py`
   → `cd N64Recomp && ./build/N64Recomp rogue_squadron.toml` (no fixup yet — clean baseline).
3. Verify the patch's regex still matches 57/57 on the fresh tree (rerun the canonical-shape
   regex from PORTING-STATE Session 454, or the saved `N64Recomp/scratch_s454_scan.py`/
   `scratch_s454_detail.py` if still present) before trusting the patch will apply cleanly.
4. `python3 fixup_game_funcs.py` — check the report line
   `funcs_3.c: doubly-linked-list append guard (DL_LIST_APPEND_GUARD) patched x26` and
   `funcs_4.c: ... patched x31` (or combined counts if file grouping differs) — audit for anomalies.
5. `cd build && cmake --build . -j8` (Metal rebuilds need
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`).
6. `strings build/roguesquadron.elf | grep -c dl-list-append-guard` sanity check (should be >=1).
7. Live-verify: full armed-var list including `ROGUESQ_LOG_DL_LIST_APPEND_GUARD=1`, phase-gated
   run (`PROBE_KEYS_FROM_PHASE=1`), SIGKILL not SIGTERM at the end. Per item -287's established
   baseline for this whole guard-idiom family: **0 fires is the norm, not an open question** —
   don't spend a session chasing a positive control that's already been established for the
   sibling families.
8. Queue a confirmation soak to `scratch/agent/soak_queue/s455_dl_list_append_confirm.sh`
   (self-contained, copy the shape of an existing recipe in `soak_queue/done/`).
9. Exit contract: PORTING-STATE.md entry, CURRENT-TRUTH.md item -292 (or renumber if the
   concurrent process already claimed -291/-292), commit.

### Also documented, not yet in scope (pick up after -0x5824 closes)
- `-0x23A8($reg)` → sibling global `0x8011DC58`, same function cluster, no clean byte-identical
  shape found (each site's downstream write differs) — needs the same S392/S393-style per-site
  mechanistic classification (check redundancy against already-active guards) before any patch.
- ~111 non-canonical `-0x5824` sites (same global `0x8011A7DC`, reached through a non-adjacent
  load/deref pair with intervening code) — needs per-site treatment, not a blanket regex.

### Confirmed non-issues, do not re-investigate
`-0x25C0($s0)` (56 sites, `mallocCraftSelectionData`) and `-0x76E0($s0)` (46 sites) are
compile-time-constant-based counter/scalar accesses (`lui $s0,0x800D` then a 16-bit counter
store/load used in index arithmetic), not pointer dereferences.

## Process/environment issue to flag to the human (not this session's job to fix)
s454 found the autonomous loop can apparently run a live iteration while a SEPARATE manually-
spawned "one iteration" session (also tagged s454) works the same repos concurrently, with no
mutual-exclusion mechanism over the shared, non-git-tracked build state
(`N64Recomp/fixup_game_funcs.py`, `RecompiledFuncs/*.c`, `build/`). This is a real collision risk
independent of any specific M3 finding — worth a human decision (don't double-spawn, or add a
lockfile) before it causes an actual corrupted build/lost edit rather than just wasted duplicate
analysis.
