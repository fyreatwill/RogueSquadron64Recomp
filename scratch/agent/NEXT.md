# NEXT work unit — M3: guard the 14th hangar-tick crash class, `reserveAndEmitDLEntry` (s109)

s108 ran the NEXT.md-prescribed `musyx-gate1` countdown/period instrument
(landed, built, armed) but got **3 consecutive soaks that all died before
the ~140s DMA window** (73.5-73.7s, well before `vi_width=640`), each to a
different hangar-tick-family crash. Per rule 8 (3 consecutive
non-discriminating attempts), that line of inquiry is parked — not
refuted, just blocked on reliability. Read PORTING-STATE.md's Session 108
entry before doing anything else; this file only has the actionable
summary.

## Why this is the next work unit, not another `musyx-gate1` soak

CURRENT-TRUTH item 0b already flagged "land a guard on the 14th or 17th
class" as the natural next step after s99-s101's 3 guards; s108's 3/3
death-before-window outcome is a second, independent data point that more
guarding is still needed before the `musyx-gate1` question can even be
tested again. Guarding is also strictly cheaper to make progress on right
now: the 14th class already has a real C-source name, a landed (but
uncapped) entry diagnostic, and a fully characterized first faulting
write — no more detective work needed before writing the fix, unlike a
blind soak that costs a full run-cycle for a coin-flip chance of reaching
the target window at all.

## What's confirmed (do not re-derive)

- `reserveAndEmitDLEntry` (`N64Recomp/RecompiledFuncs/funcs_3.c:14435`,
  guest `0x8000CB88`) is the 14th crash class (SIGBUS, s97/s98, 1
  occurrence so far), reached via the hangar-tick per-frame chain:
  `submitSceneNodeRender` ← `processSceneNode` ←
  `traverseSceneGraphRecursive` ← `setupCameraMatrices` ←
  `static_5_800AAD9C` (`runHangarSelectionFrame`) ← `static_5_800C6854`
  (`runHangarMenuFromOverlay`) ← `menuOverlayInit`.
- It already has an entry diagnostic landed (`N64Recomp/
  fixup_game_funcs.py`, `_reserve_emit_dl_entry_patch`, ~line 288,
  `funcs_3.c:14438-14447`) gated on `ROGUESQ_LOG_DLENTRY=1`, logging
  `arg_r4` (a0), `arg_r5` (a1), `ra` on every call. **It has NO cap** —
  unlike every other diagnostic in this codebase (`n < 20` style) — and
  this function is called once per scene-graph node per frame, likely
  hundreds+ of times/second. **Add a cap (`if (s_dlentry_n < 20)`,
  matching the rest of the family) before ever arming this flag in a
  soak**, or the log file will be enormous.
- Source-read the function body (`funcs_3.c:14435-14985`): `a0` (arg
  `ctx->r4`) is saved to `ctx->r16` at entry (`funcs_3.c:14456`) and
  **dereferenced as a write target almost immediately**:
  `MEM_W(0X0, ctx->r16) = 0xB5000000;` (`funcs_3.c:14478-14479`, guest
  `0x8000CBBC`-`0x8000CBC0`) then `MEM_W(0X4, ctx->r16) = 0;`
  (`funcs_3.c:14482-14487`, guest `0x8000CBC4`). **This is the first
  faulting candidate** — if `a0` is garbage/out-of-range, this write
  SIGBUSes. (`a1`/`ctx->r17` is saved but not yet dereferenced in the
  first ~90 lines of the function — lower priority, check only if guarding
  `a0` alone doesn't clear the class.)
- The function's real epilogue (register restore + return) is at
  `funcs_3.c:14971-14980` (guest `0x8000CE7C`-`0x8000CE90`): restores
  `ctx->r31`/`ctx->r17`/`ctx->r16` from the stack slots saved at entry
  (`0x18`/`0x14`/`0x10` off `ctx->r29`), undoes the `-0x20` stack
  adjustment, then `return;`. **This epilogue is NOT a clean jump target
  as-is** — it's reached by falling through real work at label
  `L_8000CE58` (`funcs_3.c:14951`, guest `0x8000CE58`) that writes to
  `a0`/`a1`-derived addresses (a different code path's cleanup, not
  generic function exit) — `goto L_8000CE58` would execute those writes
  too, which is wrong for a guard placed at function entry before those
  registers hold sane values.

## The work unit

1. **Add a cap to the existing `ROGUESQ_LOG_DLENTRY` diagnostic**
   (`N64Recomp/fixup_game_funcs.py` `_reserve_emit_dl_entry_patch`) —
   `if (s_dlentry_n < 20) { fprintf(...); } s_dlentry_n++;`, matching
   every other diagnostic in the file.
2. **Add a dedicated epilogue-only label for the guard to jump to.**
   Do not reuse `L_8000CE58`. Insert a new label immediately before the
   restore sequence, e.g. right before `// 0x8000CE7C: lw $ra, 0x18($sp)`
   (`funcs_3.c:14971`) — anchor the regex on that exact restore-sequence
   text (unique in the file: `lw $ra, 0x18($sp)` immediately followed by
   the `$s1`/`$s0` restores and `addiu $sp, $sp, 0x20` at these specific
   guest addresses) and prepend a fresh label (e.g. `L_dlentry_guard_exit:`)
   directly above it via `re.subn`, same mechanism `fixup_game_funcs.py`
   already uses elsewhere for label insertion.
3. **Add the guard immediately after the entry diagnostic block**, before
   any dereference of `ctx->r16` (i.e. right after `funcs_3.c:14456`'s
   `ctx->r16 = ADD32(ctx->r4, 0);`, or immediately after the existing
   diagnostic block, whichever is cleaner to anchor). Shape (following the
   s99-s101 convention exactly): sanity-check `U32(ctx->r4)` against a
   plausible RDRAM range (e.g. reject `< 0x80000000` or `>= 0x80800000`,
   matching whatever bound the 11th/12th/16th guards used — check their
   patches in `fixup_game_funcs.py` for the exact literal so this guard is
   consistent with the rest of the family), log a `[dlentry-guard]
   skipped` line (uncapped is fine here, it's guarded by definition to be
   rare), and `goto L_dlentry_guard_exit;` (the new label from step 2) —
   **never a bare `return;`** (skips the register restore, breaks the
   MIPS ABI for the caller).
4. **Regen order**: `python3 make_elf.py` (rogue_squadron64 dir) →
   `./build/N64Recomp rogue_squadron.toml` (N64Recomp dir, via the
   `python3 -c "import subprocess; ..."` wrapper — direct invocation of
   the binary is not allowlisted and prompts for approval) →
   `fixup_game_funcs.py` → `cmake --build`. **Full ELF regen, not a bare
   fixup re-run** (idempotency bug still unfixed, see Tooling note).
   Verify the fixup report shows the new guard patched exactly `x1` in
   `funcs_3.c` only (this file also contains other unrelated functions —
   confirm no cross-function anchor collision, per s100's lesson).
5. **Rebuild**: `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
   cmake --build build -j 8` — exit clean, only pre-existing warnings.
6. **Soak** (same repro shape, add the capped `ROGUESQ_LOG_DLENTRY=1` to
   see the guard's own control):
   `env ROGUESQ_LOG_MUSYX_DMA_CALL=1 ROGUESQ_LOG_FILL_RANGE_ARGS=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_LOG_DLENTRY=1 ROGUESQ_LOG_THREAD_RESUME=0 PROBE_MODE=start_only HOLD_S=30 zsh run_mission_keys.sh s109_dlentry_guard 30 12`
   (run from `scratch/s73_post_a_scene/`; backgrounds past the 120s
   foreground timeout — block on the task notification, don't poll).
7. **Interpret**: if the process now reaches `vi_width=640`/~140s alive
   (or at least survives past 73.5-77s where s108's 3 soaks all died),
   that's a real improvement in survival odds — re-attempt `musyx-gate1`
   next. If it still dies before the window, to a *different* crash, log
   that as the next class in the catalog and keep working down item 0b's
   list (17th class, `updateHangarBayScene`, is next in line — not yet
   source-read). If `[dlentry-guard] skipped` never fires (0/0) — that's
   informative too: `a0` was never actually bad this run, and the SIGBUS
   (if it recurs) is elsewhere in the function (check the `a1` dereference
   next, or the probable-18th `heapFreeListDequeue`-area crash s108 found
   in the same soak family — see below).

## Also flagged (s108, not this session's job but worth 1 soak's attention if convenient)

- **Probable 18th crash class** (s108, `s108_musyx_gate` run): SIGBUS,
  nearest symbol `heapFreeListDequeue + 12704`
  (`N64Recomp/RecompiledFuncs/funcs_3.c:15176`, same file as
  `reserveAndEmitDLEntry`, immediately after `reserveAlignedDLSpace`),
  same outer chain as the 14th class but **no `reserveAndEmitDLEntry`
  frame in the trace** — a different leaf, not yet source-read. Given
  `heapFreeListDequeue` is ~1700 source lines (`funcs_3.c:15176-16877`),
  the large offset may genuinely be inside this function's own body
  rather than a nearest-symbol misattribution artifact (unlike some
  other family members whose offsets clearly cross into unrelated code).
  **Only 1 occurrence — do not instrument yet** per the project's
  2nd-recurrence convention; just watch for a 2nd hit in any future soak.
- `frameStartReset` SIGBUS (s84 class, demoted at CURRENT-TRUTH item 8)
  recurred once more (s108, 2nd total occurrence). Still not dominant
  (1 in ~13 soaks). No action needed unless it starts recurring more.
- `queueGPUUploadTMEM` zero-tile-dimension assert (item 2) recurred a 7th
  time (s108, unarmed — no new diagnostic data). No action needed.

## Tooling note — still not fixed, still cheap

`fixup_game_funcs.py` is **not idempotent** by construction (every
patch's anchor regex matches text left unchanged after insertion). A
full ELF regen has now avoided the duplication symptom six times in a
row (s103-s108) as a workaround. If a session touches
`fixup_game_funcs.py` again, consider actually fixing it: make each
patch's anchor regex also require a negative lookahead that the match
is **not** immediately followed by `    { // PATCH:`. Test by running
the script twice in a row on an already-regenerated tree and confirming
the 2nd run reports 0/"no changes needed" for every already-landed
patch.

## Do not

- Do not run another blind `musyx-gate1` soak yet — 3/3 consecutive
  attempts died before the target window (rule 8). Come back to it once
  survival odds through the hangar-tick window improve (this session's
  guard work, or the next one).
- Do not re-instrument or re-soak `musyxInitVoiceFromSample`,
  `tickAudioChannel`, `serviceVoicePoolFrame`, `tickAudioSequencerFrame`,
  `tickAllAudioChannels`, or the `musyx-gate1` countdown/period site in
  isolation — all read a consistent null against either a proven-active
  surrounding system (the first 5) or an unreached window (the last one,
  s108). The open question there is unchanged: does the countdown ever
  hit 0, and is the period sane — still untested.
- Do not re-read or re-instrument `musyxKeyOnVoice`, `initSampleStreamBlockCache`,
  `fillSampleStreamRange`'s own arithmetic, `acquireSampleStreamBlock`,
  `musyxSynthFrame`'s DMA-batch call site, `submitDmaRequestBatch`, or
  `setupSongRenderBuffers` — all cleared s102-s105.
- Do not use a bare `return;` in the new guard — always `goto` a real
  epilogue label that restores saved registers, per every prior guard in
  this family (s99-s101).
- Do not compare a raw `ctx->rN` (`gpr`/`uint64_t`) value against 32-bit
  literal bounds without truncating through `U32()` first (s99's own
  lesson — a sign-extension bug made an early guard fire 100% of the
  time).
- Do not trust a `fixup_game_funcs.py` "patched xN" report without
  checking which file(s) it patched, **and do a full ELF regen first**
  if the tree may already carry prior patches.
- Do not cite `ra=0x00000000` as corruption evidence (refuted s92); do
  not re-open "random/race/stomp" framings for the `devAddr` corruption
  (7+ independent lines of evidence against all three).
- `N64Recomp/fixup_game_funcs.py` is untracked in N64Recomp's own git,
  by design — do not attempt to commit it there; the durable record
  lives in `PORTING-STATE.md`/`CURRENT-TRUTH.md` in this repo.
