# NEXT work unit

## s385 recap

Batch 8/N of the fixup_game_funcs.py function-scope-match backport: converted 16 of 17 attempted sites
across 15 functions in 8 files (funcs_1/4/14/15/23/24/26.c) — `convertMat3x4ToN64Mtx`,
`submitDmaRequestBatch`, `piDmaWorker`, `setupSongRenderBuffers`, `buildSongDecodeBufferRing`,
`musyxMixActiveVoices`, `isAudioSlotActive`, `tickAndReap3DAudioVoices`, `factor5MutexAcquire`,
`factor5MutexRelease`, `setupCameraMatrices`, `traverseSceneGraphRecursive`, `activateAnimationKeyframe`,
`setLookupEntryField5ByKey`, `initMusyXEngine`, `resetMusyXEngineState`. One site
(`tickAudioSequencerFrame`'s exit diagnostic) was correctly left file-scoped by the conversion subagent
because its match text spans past the function's own body into the next function's signature line.
Byte-identical regen-diff verified clean (no regression, unlike s384). Build clean. Soak clean (0 crash
markers over 10,757 log lines, VI reached the full 0→320→640→1024 timeline at 45.5s, held at 1024 for
~1500 further frames before SIGKILL). **Running total: 164/176 converted, 12 remain.**

**Process finding**: when delegating site identification to an Explore agent, the standing exclusion list
must be given by address/anchor (e.g. `0x8008EC88`), not just by function name — this session's Explore
agent's recommended batch included the volatile `reapplyDisplayMode` audio-gate hand patch because it
wasn't named by address in the prompt. Caught by the orchestrating session reading the patch's own comment
before delegating conversion; no bad edit ever reached a subagent. Apply this the same way next time:
before delegating identification, re-state every standing exclusion as an address/anchor string, not just
a function name.

## What's actually left (12 sites)

Re-scanned and triaged as of s385. Of the 12 remaining bare file-scoped sites, **9 are confirmed
intentional design exclusions**, not backlog:
1. Line ~55 — whole-file `$zero`-write comment-out sweep (~2700 sites). Never convert.
2. Line ~269 — `0x8008EC88` `reapplyDisplayMode` audio-gate hand patch. Actively volatile/experimental,
   file-scoped on purpose.
3. Lines ~346/428 — `waitForMusyXAudioTaskDone`/`shutdownAudioEngine` pair. Deliberately dual-target.
4. Line ~5560 — `_s284_deref_guard_sites` multi-function guard loop. Deliberately multi-function.
5. Line ~8647 — `runHangarMenuFromOverlay`/`hasKasanMoorDefected` bare-label collision. Needs a dedicated
   `p.name`-filter fix, not this backport's idiom — a SEPARATE small work unit, not part of "converted."
6. Line ~11833 (s385) — `tickAudioSequencerFrame`'s exit diagnostic. Match text spans past this function's
   own body into the next function's signature; can't be body-scoped without breaking it.
7. Line ~11996 — `musyxSynthFrame`'s `synth-rearm-ptr` diagnostic. Real anchor lives inside
   `initN64RspMixer`, not this function; deliberately left file-scoped pending a separate investigation
   into which function should actually own the diagnostic.

**3 remaining sites are genuinely untriaged** — named as follow-up candidates by s385's Explore agent but
not yet confirmed body-span-checked or converted: `mat3x3InverseInto` (funcs_5.c, ~line 9468 pre-batch8),
`tickTextureMaterialExpiry` (funcs_6.c, ~line 10313 pre-batch8), `coalesceFreeHeapBlocks` (funcs_0.c,
~line 11435 pre-batch8). Re-locate exact current line numbers with a fresh `scan_filescoped.py` run before
acting — numbers shift every batch.

## This iteration's work unit: batch 9/N — the last 3 untriaged sites, OR close out the backport

### Option A (preferred if the 3 sites convert cleanly): batch 9

1. `cd ~/Documents/Tools/N64Recomp && python3 scratch_batch3/scan_filescoped.py` — confirm 12 remain, get
   fresh line numbers.
2. Since there are only 3 candidate sites and they're already named, identification can be done directly
   in the orchestrating session (grep each function's `RECOMP_FUNC` signature in the corresponding
   `RecompiledFuncs/funcs_N.c`, confirm the patch's regex anchor falls within that function's body span via
   the same `func_re`-boundary check used every batch) — no need to spin up a separate Explore agent for
   only 3 sites.
3. Delegate ONLY the conversion step to a general-purpose subagent (same idiom, same backup-file convention:
   `cp fixup_game_funcs.py fixup_game_funcs.py.pre-scope-backport-backup-batch9`), same "do not force a
   mismatched conversion through" standing rule.
4. Verify in the orchestrating session: clear `RecompiledFuncs/`, regen (make_elf.py + N64Recomp) twice
   (pre-batch9 backup script vs. new script), diff both the fixup-report and the tree — byte-identical
   required.
5. Build (`DEVELOPER_DIR=... cmake --build build -j8`), soak (wrapper-script method, Monitor for
   place-your-ROM sanity / VI width transitions / crash markers, `ps aux | grep -i roguesquadron` + `kill
   -9` the real PID). Expect the same clean shape as batches 1-8.
6. If all 3 convert cleanly: **176 - 9 intentional exclusions = 167 theoretically-convertible sites, all
   167 done.** The backport is functionally COMPLETE at that point — the remaining 9 sites are permanent by
   design, not future batches. Update CURRENT-TRUTH to say so explicitly and retire this as a recurring
   "sanctioned tooling" work unit (still available to revisit only if one of the 2 SEPARATE follow-up items
   below gets picked up).

### Option B (if any of the 3 sites turns out to be another `tickAudioSequencerFrame`-style non-fit):
document why in PORTING-STATE the same way s384/s385 did, leave it file-scoped, and still close out the
backport with whatever the final convertible count is — don't force it.

### Two SEPARATE follow-up items, not part of this backport's scope, worth their own future work units:
- **`runHangarMenuFromOverlay`/`hasKasanMoorDefected` collision fix**: needs `p.name` filtering added to
  that one file-scoped patch (restrict the match to whichever overlay file the intended function actually
  lives in), not a function-scope conversion. Small, well-scoped, safe to pick up once the main backport is
  closed.
- **`musyxSynthFrame`/`initN64RspMixer` `synth-rearm-ptr` ownership question**: does the
  `ROGUESQ_LOG_AUDIOTICK_TRACE`-gated diagnostic at `0x800919D4` genuinely belong in `initN64RspMixer`
  instead of `musyxSynthFrame`? Not urgent (diagnostic isn't armed in any soak recipe), but worth a source
  read next time someone's in that region of the M5 audio code.

## Iteration budget

HYPOTHESIS-ID: fixup-scope-backport (iteration 10 of an open-ended bounded tooling task). 12 remain, 9 of
which are confirmed intentional exclusions as of s385 — this task is close to fully closed out. Batch 9
(3 sites) should be the last real conversion batch; after it, either declare the backport complete or park
whatever residual sites don't fit the idiom, and move attention to the two follow-up items above or back to
the top of the strategic-priority stack (M5 audio has no open thread as of s376; M3 crash work is next in
line per the user directive if this tooling task closes out).
