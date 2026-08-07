# NEXT work unit

HYPOTHESIS-ID: dl-list-append-guard-5824

## s454/s455 close-out: the concurrent-process collision is RESOLVED, both findings are real

Sessions 454 and 455 were two ends of the same collision: `tools/agent/loop.sh`'s own spawned
iteration (committed as `013c95d`, tagged "s454" in the ledger) and an interactive session working
the identical mandate at the same time (committed separately, tagged "s455" in the ledger) both
independently opened a fresh M3 idiom-class audit and both found real, different, non-overlapping
idiom classes. By the time s455 reached its own exit contract, `013c95d` had already landed
cleanly and the collision was confirmed OVER (`ps`/`loop.log` showed `loop.sh`'s spawned `claude`
process had exited; no live process was mutating shared state anymore). Full trail: `PORTING-STATE.md`
Sessions 454 and 455, `docs/CURRENT-TRUTH.md` items -291 and -292.

**Do NOT re-open the "is loop.sh still running" question as a blocker** unless you find fresh
evidence of it (check `ps aux | grep loop.sh` and `tail -20 scratch/agent/loop.log` once, cheaply,
at the start of this session, same as always — but don't treat the s454/s455 collision itself as
still-open; it's resolved and reconciled in the ledger).

## Priority 1: execute item -291's already-designed `DL_LIST_APPEND_GUARD` (fast, no design work left)

`fixup_game_funcs.py` (`N64Recomp` repo, untracked — not `export.sh`'d, doesn't need to be) already
has a `DL_LIST_APPEND_GUARD` patch block (search for that string to find it) targeting a
doubly-linked-list-append idiom at `-0x5824($reg)` → global `0x8011A7DC` (`lui $reg, 0x8012`), 57
verified sites across `funcs_3.c` (26) and `funcs_4.c` (31) — `allocateDisplayListBuffer`,
`emitFrameRdpInitDl`, `emitColorFillRect`, `drawFrameProfilerBars`, `emitMaterialTexturedDLAlt`,
`renderFlatMeshFaceGroup`, `buildOrientedFaceGeometry`, `renderLitMeshFaceGroup`,
`drawTextGlyphRect`, `drawSubtitleText`, `setupCameraMatrices`. This is DESIGN-COMPLETE, written,
syntax-checked — it just needs the standard pipeline run:

1. Raw regen for a clean baseline: delete `N64Recomp/RecompiledFuncs/funcs_*.c` (use
   `python3 -c "import glob,os; [os.remove(f) for f in glob.glob('.../funcs_*.c')]"` if `rm` with a
   glob gets blocked by the sandbox — it did for s455), then `cd rogue_squadron64 && python3
   tools/make_elf.py`, then (separately, working-directory-persisted, NOT chained with `&&` +
   redirection — that combination gets blocked; `cd` once, then run the binary in its own call)
   `cd N64Recomp && ./build/N64Recomp rogue_squadron.toml`.
2. `python3 fixup_game_funcs.py` — check the report for
   `funcs_3.c: doubly-linked-list append guard (DL_LIST_APPEND_GUARD) patched x26` and
   `funcs_4.c: ... patched x31` (or however the counts land — audit for anomalies per the standing
   item -20 rule, don't just trust an expected number).
3. `cd RogueSquadron64Recomp/build && cmake --build . -j8` (Metal rebuilds need
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`).
4. `strings build/roguesquadron.elf | grep -c dl-list-append-guard` (or whatever the actual log tag
   is — check the patch text) sanity check.
5. Live-verify: `tools/probe.sh`, full armed-var list (see `scratch/agent/soak_queue/done/` for a
   recent recipe to copy the exact env-var list from — always arm ALL passive guard vars, never
   rotate one per soak) plus `ROGUESQ_LOG_DL_LIST_APPEND_GUARD=1`, `PROBE_KEYS_FROM_PHASE=1`,
   SIGKILL at teardown. Per item -287's established baseline for this whole guard-idiom family: 0
   fires is the norm, not an open question.
6. Queue confirmation soak to `scratch/agent/soak_queue/s456_dl_list_append_confirm.sh`.
7. Exit contract: PORTING-STATE.md entry, CURRENT-TRUTH.md item -293, commit.

## Priority 2 (if time remains after -291, or a future session): finish item -292's SONGTEMPO_TABLE_GUARD

`updateSongTempoTickRate` (4/43 sites) is DONE and verified (s455). The remaining 39 sites are the
same `0x29C0($reg)` → global `0x801529C0` MusyX song-track-pointer idiom, in 5 more reader
functions, all in `funcs_25.c`:
- `tickScheduledSongEvents` (5 sites, ~200 lines)
- `stepSongPitchBendLanes` (5 sites, ~279 lines)
- `stepSongModulationLanes` (5 sites, ~283 lines)
- `advanceSongRegion` (12 sites, ~539 lines)
- `stepActiveSongTracks` (12 sites, ~744 lines)

Do the two smallest (`tickScheduledSongEvents`, `stepSongPitchBendLanes`) next, same session if
time allows — same method as `updateSongTempoTickRate`: **read the whole function body first**,
identify each site's real bail semantics (before-prologue → bare `return;`; inside an existing
loop with its own exit label → reuse that label; past all loops, near the real epilogue →
duplicate the epilogue) — do NOT templatize blindly, each function's control flow differs. The two
largest (`advanceSongRegion`, `stepActiveSongTracks`) are unusually large and their tail sections
showed an odd stack-frame mismatch on a first skim (prologue pushes more than the visible epilogue
pops) — worth checking for the recompiler's cross-function shared-tail-merge behavior (seen
elsewhere as `lvj_checkComplexObjectives`/`audioCompandS16`/`__OSGlobalIntMask`, CLAUDE.md) before
trusting a single simple bail-to-epilogue pattern; may need per-site individual verification rather
than a uniform template.

## Confirmed non-issues, do not re-investigate

`-0x25C0($s0)` (56 sites, `mallocCraftSelectionData`) and `-0x76E0($s0)` (46 sites, spread across
8 files) are compile-time-constant-based counter/scalar accesses (`lui $s0, 0x800D` then a 16-bit
counter store/load used in index arithmetic), not pointer dereferences — independently confirmed
by both s454 and s455.

Small/ubiquitous offsets (`0x0`, `0x4`, `0x8`, `0xC`, `0x10`, `0x14`, `0x18`, `0x1C`, `0x20`...)
match hundreds of unrelated functions doing ordinary struct-field access — too broad to be a
distinct idiom class the way `-0x25A4`/`-0x5824`/`0x29C0` are (large, distinctive, concentrated in
a narrow subsystem). Don't re-run a plain frequency scan without the concentration filter
(`|offset| >= 0x1000`, small function count) — it just reproduces this noise.

`-0x23A8($reg)` → sibling global `0x8011DC58` (same `funcs_3.c`/`funcs_4.c` cluster as item -291,
but each site's downstream write differs — no clean byte-identical shape found) needs the same
S392/S393-style per-site mechanistic classification before any patch, not a blanket regex. Not
started.

## Process note carried forward (both s454 and s455 hit this independently)

If you delegate this whole work unit to a background subagent, watch for the subagent itself
reflexively delegating further instead of executing — it happened this session (the first spawned
subagent reported "I've delegated this to another subagent, I'll wait" and returned immediately
with no real work done; a SECOND, nested subagent it apparently spawned did the actual work ~18
minutes later, unprompted by the orchestrator). If a subagent's report reads like a
plan/promise rather than a completed result, check actual repo state (`git log`, file mtimes)
before trusting it — don't assume "completed" status means real work happened.
