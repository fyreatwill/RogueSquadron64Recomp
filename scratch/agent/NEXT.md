# NEXT work unit

## s384 recap

Batch 7/N of the fixup_game_funcs.py function-scope-match backport: converted 17 (not the planned 18)
sites across 9 functions in 8 files — `musyxSynthFrame`, `initFactor5Mutex` (funcs_24.c),
`update3DAudioFrame` (funcs_26.c), `tickAllActiveSongs` (funcs_25.c), `viRetraceHandlerThread` (funcs_4.c),
`waitForPostSwapAck` (funcs_5.c), `updateAnimatedTextureStreaming` (funcs_11.c), `static_5_800B4048`
(funcs_41.c), `selectPostCrawlCraft` (funcs_30.c). Identification delegated to a read-only Explore
subagent (per s382's process), conversion delegated to a general-purpose subagent.

**This batch's verification step did its actual job, not just a formality**: the byte-identical
regen-diff check found a real drop — `musyxSynthFrame`'s `[synth-rearm-ptr]` diagnostic went from 1 match
(file-scoped, pre-batch7) to 0 matches (scoped to `musyxSynthFrame`'s body, post-batch7). Root cause,
confirmed with a standalone script re-deriving the same `func_re`-boundary slice the fixup script itself
uses: the `0x800919D4` anchor this patch matches on occurs exactly ONCE in the whole of `funcs_24.c`, and
it falls INSIDE `initN64RspMixer` (the function immediately following `musyxSynthFrame`), not inside
`musyxSynthFrame` as both the batch-7 conversion AND an old s101-era design comment (in the audio-tick-
trace block, ~line 11499 of the pre-batch7 file) both assumed. **This means the original design comment
was already wrong** before this session touched anything — the file-scoped patch "worked" for years by
accident, matching text anywhere in the file regardless of which function it was actually in. Fix applied:
reverted that ONE site to its original file-scoped form (byte-identical to pre-batch7 behavior), left it
OUT of the batch's converted-count, added an inline comment explaining the discrepancy. Re-verified
byte-identical after the fix (both fixup-report diff and full-tree diff -rq empty). Build clean. Soak
clean (0 crash markers, VI reached the full 0→320→640→1024 timeline in 45.6s, matching batch 6 almost
exactly). **Running total: 148/176 converted, 28 remain.**

**Open finding to consider, not urgent**: is the `0x800919D4` read genuinely meant to characterize
`musyxSynthFrame`'s self-re-arm behavior (per the s101-era hypothesis), or does the diagnostic actually
need to live in `initN64RspMixer` instead? Nobody has revisited this since s101. Since the diagnostic is
env-var-gated (`ROGUESQ_LOG_AUDIOTICK_TRACE`) and not currently armed in any soak recipe, this is safe to
leave alone — flagging only so a future M5-audio session doesn't trust the old comment's function
attribution at face value.

## This iteration's work unit: fixup_game_funcs.py function-scope-match backport, batch 8/N

### Concrete steps

1. Regenerate the current inventory (line numbers shift every batch). In `~/Documents/Tools/N64Recomp/`:
   ```
   python3 scratch_batch3/scan_filescoped.py
   ```
   Should print 28 remaining sites.
2. Identify target functions for a batch of ~15-25 sites. Delegate to a read-only Explore/general-purpose
   subagent (same method as s382-s384: give it the fresh site line-number list, ask it to grep each site's
   MIPS address in `RecompiledFuncs/funcs_*.c`, walk up to the nearest `RECOMP_FUNC void <Name>(` anchor,
   and flag excluded classes / multi-function-loop sites / unresolved collisions). **Explicitly instruct it
   to verify each candidate anchor actually falls WITHIN the target function's body (compute the body span
   via the same func_re-boundary method used by the fixup script itself, don't just eyeball line-number
   proximity)** — s384 found a case where a decades-old design comment had the wrong function attribution
   and only the mechanical body-boundary check caught it. s383's identification pass already named 20+
   single-site candidate functions from the 39-site pool it scanned (see PORTING-STATE Session 383/384 for
   the list: setupSongRenderBuffers, buildSongDecodeBufferRing, initMusyXEngine, resetMusyXEngineState,
   tickAudioSequencerFrame, musyxMixActiveVoices, isAudioSlotActive, factor5MutexAcquire,
   factor5MutexRelease, tickAndReap3DAudioVoices, convertMat3x4ToN64Mtx, setupCameraMatrices,
   traverseSceneGraphRecursive, submitDmaRequestBatch, piDmaWorker, loadCraftShadowTextures,
   mat3x3InverseInto, activateAnimationKeyframe, setLookupEntryField5ByKey, tickTextureMaterialExpiry,
   coalesceFreeHeapBlocks) — re-confirm against the fresh 28-site scan since line numbers shift every
   batch, but this is a good starting point; all were single-site (no clustering benefit) so batch by
   whichever ~15-20 fit best, prioritizing the funcs_23.c/funcs_24.c/funcs_26.c audio cluster
   (setupSongRenderBuffers, buildSongDecodeBufferRing, initMusyXEngine, resetMusyXEngineState,
   tickAudioSequencerFrame, musyxMixActiveVoices, isAudioSlotActive, factor5MutexAcquire,
   factor5MutexRelease, tickAndReap3DAudioVoices — 10 functions, likely 10-12 sites) since it's already in
   one region of the file.
3. **Delegate ONLY the conversion step** to a subagent (general-purpose, default model): give it the exact
   site line numbers/range, the target function names identified in step 2, and the conversion idiom
   (locate `RECOMP_FUNC void <Name>(...)` anchor, slice the function body via the SAME brace-matching
   helper already used at any converted site — e.g. `acquireSampleStreamBlock` — run the SAME regex
   pattern/replacement against `body` instead of `text`, splice back). **Explicitly tell it to use THIS
   session's number in any new `# (scoped, sNNN backport)` comment tag it writes, not to copy the number
   from an existing example conversion it's pattern-matching against** (s384 process note: the subagent
   copied "s383" verbatim into all of batch 7's new comments — cosmetic, but avoid repeating it). Back up
   first: `cp fixup_game_funcs.py fixup_game_funcs.py.pre-scope-backport-backup-batch8` (leave batches
   1-7's backups in place). Tell the subagent explicitly: do NOT attempt verification, build, or soak; do
   NOT touch the multi-function loop site or the runHangarMenuFromOverlay collision site if either ended up
   in scope by mistake; report back once conversion edits are made and the AST scan confirms the expected
   count drop.
4. **Verify in the orchestrating session** (not delegated) — treat this as a REAL check, not a formality;
   s384 found a genuine regression here:
   - Clear `RecompiledFuncs/funcs_*.c`:
     `python3 -c "import pathlib; [p.unlink() for p in pathlib.Path('RecompiledFuncs').glob('funcs_*.c')]"`
     (glob `rm -f` needs approval in this sandbox; this one-liner does not).
   - Pass A: `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`, then (separately, `cd`
     first as its own command — chaining `cd X && cmd` into one Bash call gets blocked by the sandbox as
     an ambiguous-cwd compound command) `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp
     rogue_squadron.toml`, then `python3 fixup_game_funcs.py.pre-scope-backport-backup-batch8 >
     scratch_batch8/report_before.txt 2>&1`, then snapshot the tree: `python3 -c "import shutil;
     shutil.copytree('RecompiledFuncs', 'scratch_batch8/RecompiledFuncs-before')"`.
   - Clear `funcs_*.c` again, regen again (make_elf.py + N64Recomp), then Pass B: `python3
     fixup_game_funcs.py > scratch_batch8/report_after.txt 2>&1`.
   - `diff scratch_batch8/report_before.txt scratch_batch8/report_after.txt` and `diff -rq
     scratch_batch8/RecompiledFuncs-before RecompiledFuncs` — BOTH must be empty. **If either is NOT
     empty**, do what s384 did: find the exact missing/changed report line, grep its anchor text in the
     regenerated `RecompiledFuncs/funcs_*.c`, and check with a standalone Python snippet whether the
     anchor actually falls within the target function's `func_re`-derived body span. If it doesn't, revert
     that one site to file-scoped (matching its original proven-correct behavior), drop it from the
     batch's converted-count, and re-verify. Do not force a mismatched conversion through.
5. Build: `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
   ~/Documents/Tools/RogueSquadron64Recomp/build -j8`. Must succeed (pre-existing `DDIV`/`DMULT`
   sign-conversion warnings are harmless and expected, not new).
6. Soak in the orchestrating session — use the wrapper-script fix, NOT a bare inline command:
   ```
   cat > scratch_batch8/run_soak.sh <<'EOF'
   #!/bin/bash
   export ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1
   cd ~/Documents/Tools/RogueSquadron64Recomp/build
   exec ./RogueSquadron64Recomp
   EOF
   ```
   then launch with `zsh scratch_batch8/run_soak.sh > scratch_batch8/soak.log 2>&1` via `Bash
   run_in_background: true`. Immediately check the first ~10 log lines for the "place your ROM"
   placeholder message (if present, the launch cwd is wrong — stop and fix before trusting anything else).
   Use the Monitor tool to wait for `vi_width=1024` or a crash marker rather than foreground-sleeping (a
   foreground `sleep` command is blocked by the sandbox — use `Bash run_in_background: true` with a loop,
   or the Monitor tool, to wait). Then grep the full log for crash markers
   (`UnhandledJumpTarget|\[defer-drop\]|\[dmem-race\]|Assertion|SIGSEGV|SIGBUS|SIGTRAP|CRASH`), find the
   real game PID via `ps aux | grep -i roguesquadron` (not the shell wrapper — `pgrep -f
   "build/RogueSquadron64Recomp"` failed to match in s383, use `ps aux` instead if it comes up empty), and
   `kill -9` it. Expect 0 crash markers and VI reaching 1024, same as every batch so far.
7. Site-classes correctly EXCLUDED from any batch, still: the `0x8008EC88` audio-gate durable hand patch;
   the `waitForMusyXAudioTaskDone`/`shutdownAudioEngine` pair; the whole-file `$zero` sweep (~line 55); the
   multi-function `_s284_deref_guard_sites` loop; the `runHangarMenuFromOverlay`/`hasKasanMoorDefected`
   collision site (needs its own `p.name`-filter fix, not this backport's idiom — resurfaced again in
   s384's fresh scan, still deferred); the `musyxSynthFrame`/`initN64RspMixer` `[synth-rearm-ptr]` site
   (reverted to file-scoped in s384, needs a dedicated investigation into which function actually owns it,
   not a mechanical conversion).

### Expected outcome

Same shape as batches 1-7: clean conversion (delegated) + byte-identical verification + clean build +
clean soak (all three run directly by the orchestrating session) — write up as ADVANCED. Or another genuine
anchor-attribution mismatch caught by verification (also valuable — s384 found one, treat it as a real
possibility, not a hypothetical, and handle it the same way: revert the one site, keep the rest of the
batch, document the finding).

## Iteration budget

HYPOTHESIS-ID: fixup-scope-backport (iteration 9 of an open-ended bounded tooling task — not a hypothesis
chase, the usual 3-iteration pivot pressure doesn't apply the same way, but keep naming it for the loop's
bookkeeping). 28 remain after 7 real batches (23/21/24/21/21/21/17 per batch, s380 was a maintenance
iteration) — roughly 1-2 more batches at this rate, plus the parked `runHangarMenuFromOverlay` collision
fix and the `synth-rearm-ptr` attribution question as possible separate small units once the main backport
closes out.
