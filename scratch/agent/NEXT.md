# NEXT work unit

## s383 recap

Batch 6/N of the fixup_game_funcs.py function-scope-match backport: converted 21 more sites, all in
`funcs_4.c` — `processSceneNode` ×10, `renderUnlitMeshFaces` ×7, `drawSubtitleText` ×2,
`evalCubicSplineAtTime` ×2. Identification delegated to a read-only Explore subagent (per s382's process
finding), which returned a full 66-row table plus the recommended batch. Conversion delegated to a
general-purpose subagent. Verified byte-identical (fixup report + full RecompiledFuncs tree, both
zero-diff), built clean, soaked clean (0 crash markers, VI reached the full 0→320→640→1024 timeline in
45.6s, ran steady at 1024 for ~40s before SIGKILL). **Running total: 131/176 converted, 45 remain.**

**Two findings from the identification pass, read before batch 7:**
1. **Genuine latent collision at ~line 8299** (`runHangarMenuFromOverlay`): its file-scoped `subn`
   pattern matches a bare label anchor (`L_800C68AC:`) that ALSO occurs, textually identically, in an
   unrelated function `hasKasanMoorDefected` in a different overlay file (`funcs_29.c`). Today's
   file-scoped patch silently double-targets both. This is NOT a simple function-scope conversion
   candidate (there's no single enclosing function to slice to) — it needs an explicit `p.name ==
   "funcs_43.c"` filter added to scope it to the intended file only, a different fix shape than the rest
   of this backport. Left untouched in batch 6. Worth a dedicated look, possibly as its own small work
   unit before or alongside a future batch (decide: is patching `hasKasanMoorDefected` too actually
   harmless collateral, or does it need suppressing?).
2. **The `initFactor5Mutex`-adjacent region (lines ~7930-8006, ~11163-11357) is 6+ distinct functions**,
   not one — `initFactor5Mutex`, `factor5MutexAcquire`, `factor5MutexRelease`, `initMusyXEngine`,
   `resetMusyXEngineState`, `update3DAudioFrame`, `tickAllActiveSongs`, `tickAudioSequencerFrame`,
   `viRetraceHandlerThread`, `musyxSynthFrame` — despite being close together in the file. A prior
   session's naive nearest-anchor scan wrongly attributed ~30 sites to a single distant
   `initFactor5Mutex` anchor. Each of these functions individually has only 1-2 sites, so they're small
   but numerous — a good candidate for batch 7 since address-grep identification is already done (see
   s382's subagent report, reproduced in PORTING-STATE Session 382 if not already migrated) — just needs
   re-confirming against the fresh scan since line numbers shift every batch.

## This iteration's work unit: fixup_game_funcs.py function-scope-match backport, batch 7/N

### Concrete steps

1. Regenerate the current inventory (line numbers shift every batch). In `~/Documents/Tools/N64Recomp/`:
   ```
   python3 scratch_batch3/scan_filescoped.py
   ```
   Should print 45 remaining sites.
2. Identify target functions for a batch of ~15-25 sites. Delegate to a read-only Explore/general-purpose
   subagent (same method as s382/s383: give it the fresh site line-number list, ask it to grep each site's
   MIPS address in `RecompiledFuncs/funcs_*.c`, walk up to the nearest `RECOMP_FUNC void <Name>(` anchor,
   and flag excluded classes / multi-function-loop sites / unresolved collisions). Recommended focus per
   the s383 findings above: the `initFactor5Mutex`-adjacent region's 9-10 distinct small functions should
   sum to a reasonable batch on their own, or combine with whatever the next-largest fresh cluster is.
   Known items to explicitly exclude from any batch: the `_s284_deref_guard_sites` multi-function loop
   (still needs its own dedicated per-address-splitting batch — has not shrunk, still ~4 sites folded into
   1 site count in the AST scan since it's a single `subn` call inside a Python loop); the `~8299`
   `runHangarMenuFromOverlay`/`hasKasanMoorDefected` collision (needs the different `p.name`-filter fix
   described above, not a function-scope conversion — do NOT fold into a normal batch).
3. **Delegate ONLY the conversion step** to a subagent (general-purpose, default model): give it the exact
   site line numbers/range, the target function names identified in step 2, and the conversion idiom
   (locate `RECOMP_FUNC void <Name>(...)` anchor, slice the function body via the SAME brace-matching
   helper already used at any converted site — e.g. `acquireSampleStreamBlock` — run the SAME regex
   pattern/replacement against `body` instead of `text`, splice back). Back up first: `cp
   fixup_game_funcs.py fixup_game_funcs.py.pre-scope-backport-backup-batch7` (leave batches 1-6's backups
   in place). Tell the subagent explicitly: do NOT attempt verification, build, or soak; do NOT touch the
   multi-function loop site or the runHangarMenuFromOverlay collision site if either ended up in scope by
   mistake; report back once conversion edits are made and the AST scan confirms the expected count drop.
4. **Verify in the orchestrating session** (not delegated):
   - Clear `RecompiledFuncs/funcs_*.c`:
     `python3 -c "import pathlib; [p.unlink() for p in pathlib.Path('RecompiledFuncs').glob('funcs_*.c')]"`
     (glob `rm -f` needs approval in this sandbox; this one-liner does not).
   - Pass A: `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`, then (separately, `cd`
     first as its own command — chaining `cd X && cmd` into one Bash call gets blocked by the sandbox as
     an ambiguous-cwd compound command) `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp
     rogue_squadron.toml`, then `python3 fixup_game_funcs.py.pre-scope-backport-backup-batch7 >
     scratch_batch7/report_before.txt 2>&1`, then snapshot the tree: `python3 -c "import shutil;
     shutil.copytree('RecompiledFuncs', 'scratch_batch7/RecompiledFuncs-before')"`.
   - Clear `funcs_*.c` again, regen again (make_elf.py + N64Recomp), then Pass B: `python3
     fixup_game_funcs.py > scratch_batch7/report_after.txt 2>&1`.
   - `diff scratch_batch7/report_before.txt scratch_batch7/report_after.txt` and `diff -rq
     scratch_batch7/RecompiledFuncs-before RecompiledFuncs` — BOTH must be empty.
5. Build: `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
   ~/Documents/Tools/RogueSquadron64Recomp/build -j8`. Must succeed (pre-existing `DDIV`/`DMULT`
   sign-conversion warnings are harmless and expected, not new).
6. Soak in the orchestrating session — use the wrapper-script fix, NOT a bare inline command:
   ```
   cat > scratch_batch7/run_soak.sh <<'EOF'
   #!/bin/bash
   export ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1
   cd ~/Documents/Tools/RogueSquadron64Recomp/build
   exec ./RogueSquadron64Recomp
   EOF
   ```
   then launch with `zsh scratch_batch7/run_soak.sh > scratch_batch7/soak.log 2>&1` via `Bash
   run_in_background: true`. Immediately check the first ~10 log lines for the "place your ROM"
   placeholder message (if present, the launch cwd is wrong — stop and fix before trusting anything else).
   Use the Monitor tool to wait for `vi_width=1024` or a crash marker rather than foreground-sleeping. Then
   grep the full log for crash markers
   (`UnhandledJumpTarget|\[defer-drop\]|\[dmem-race\]|Assertion|SIGSEGV|SIGBUS|SIGTRAP|CRASH`), find the
   real game PID via `ps aux | grep -i roguesquadron` (not the shell wrapper — `pgrep -f
   "build/RogueSquadron64Recomp"` failed to match in s383, use `ps aux` instead if it comes up empty), and
   `kill -9` it. Expect 0 crash markers and VI reaching 1024, same as every batch so far.
7. Site-classes correctly EXCLUDED from any batch, still: the `0x8008EC88` audio-gate durable hand patch;
   the `waitForMusyXAudioTaskDone`/`shutdownAudioEngine` pair; the whole-file `$zero` sweep (~line 55); the
   multi-function `_s284_deref_guard_sites` loop; the `runHangarMenuFromOverlay`/`hasKasanMoorDefected`
   collision site (needs its own `p.name`-filter fix, not this backport's idiom).

### Expected outcome

Same shape as batches 1-6: clean conversion (delegated) + byte-identical verification + clean build +
clean soak (all three run directly by the orchestrating session) — write up as ADVANCED. Or a genuine
latent-collision finding at one specific site (also valuable, write up and exclude that site — batch 6
already found one, so treat this as a real possibility, not a hypothetical).

## Iteration budget

HYPOTHESIS-ID: fixup-scope-backport (iteration 8 of an open-ended bounded tooling task — not a hypothesis
chase, the usual 3-iteration pivot pressure doesn't apply the same way, but keep naming it for the loop's
bookkeeping). 45 remain after 6 real batches (23/21/24/21/21/21 per batch, s380 was a maintenance
iteration) — roughly 2 more batches at this rate, plus the parked `runHangarMenuFromOverlay` collision fix
as a possible separate small unit.
