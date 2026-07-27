# NEXT work unit — M3: find and fix the `musyxSynthFrame` DMA field bug (s102)

s101 closed the 7-session-old "who calls `submitDmaRequestBatch`
indirectly" question: it's `musyxSynthFrame` (a per-VI-retrace audio
tick), called from `viRetraceHandlerThread`. It also landed and validated
the 11th crash class's guard (`projectModelBoundsToScreen`, clean 0/0
negative control). Read PORTING-STATE.md's Session 101 entry before doing
anything else; this file only has the actionable summary.

## The work unit

Source-read `musyxSynthFrame`'s indirect call and `submitDmaRequestBatch`'s
signature to find the exact field-mapping bug, then fix it at the source
(N64Recomp/fixup_game_funcs.py), guest-side.

1. **Read `submitDmaRequestBatch`'s own body first** — its address is
   guest `0x8000569C`; find it in `N64Recomp/RecompiledFuncs/` (grep for
   `0x8000569C:` in the file `funcs_1.c`, per s93's discovery of the ring
   producer). Confirm which of its arguments (`a0`-`a3`) maps to the
   `devAddr` field the ring-producer log already prints (`ROGUESQ_LOG_
   DMA_RING`'s `[dma-ring-producer]` line, `dma-ring-producer` fprintf
   site in `fixup_game_funcs.py`) — this tells you which register at the
   call site is the one carrying garbage.
2. **Read the call site**: `N64Recomp/RecompiledFuncs/funcs_24.c:3856-
   3875`, inside `musyxSynthFrame` (starts at `funcs_24.c:3095`). As of
   s101 this is known to set up (all relative to `G_BASE = 0x8015<<16`):
   `a0 = MEM_W(G_BASE - 0x68D8)`, `a1 = MEM_HU(G_BASE - 0x68DC)` (a
   flag/count gating whether this branch even runs), `a2 = G_BASE -
   0x68D0` (an address, not a loaded value), target function pointer
   `v1 = MEM_W(G_BASE - 0x6624)`. Cross-reference against step 1's answer
   to see which of a0/a1/a2 is supposed to be `devAddr` and what it
   actually contains.
3. **Discriminating instrument** (batch instrument everything in one
   build/run per ITERATION.md's rule): add a log at the `musyxSynthFrame`
   call site (new `ROGUESQ_LOG_MUSYX_DMA_CALL=1` flag, same pattern as
   every prior guard/log in `fixup_game_funcs.py`) that prints the raw
   values of whichever registers map to a0-a2 right before the call,
   **plus** the values at a few neighboring offsets of whichever global
   struct `G_BASE-0x68D8`/`-0x68D0` live in (±4/±8 bytes) — if a
   neighboring field (e.g. a sample/instrument name-table pointer)
   matches the corrupted `devAddr` the ring-producer log shows
   bit-for-bit, that names the exact wrong-offset bug. The existing
   `[dma-ring-producer]` log already prints the corrupted value on the
   other end of the same call in the same run — no need to guess, just
   compare the two logs from one soak.
4. **If a wrong-offset/wrong-field bug is confirmed**: the fix is
   guest-side, in `N64Recomp/fixup_game_funcs.py` (a hand-patch
   correcting the offset used to load the value that becomes `devAddr`,
   or correcting which struct member gets passed as the DMA-batch
   argument) — follow the same "patch text anchored on the exact
   instruction, file-scoped, verify `patched x1` in exactly the expected
   file" discipline as every guard patch this session and last (s99-101).
   **If the mechanism turns out NOT to be a simple wrong-offset read**
   (e.g. it's a genuine race between two threads touching the same
   global, or a legitimately variable value that's supposed to be
   interpreted differently) — characterize that instead of forcing a fix
   that doesn't match the evidence; a correct root-cause writeup is a
   valid outcome even without a fix landed this session.
5. Regen order if any `RecompiledFuncs/*.c` changes are needed beyond the
   fixup script (unlikely — this should be a `fixup_game_funcs.py`-only
   change like every guard so far): `make_elf.py` → `N64Recomp` →
   `fixup_game_funcs.py` → `cmake --build`. If only editing
   `fixup_game_funcs.py`, re-running it alone against the existing
   `RecompiledFuncs/` is enough (same as every guard session).
6. Rebuild: `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j 8` — exit clean (only the pre-existing-class format/sign warnings).
7. Soak with the full flag set plus every family instrument (all free,
   keep them all armed) plus the new `ROGUESQ_LOG_MUSYX_DMA_CALL=1`:
   ```
   env ROGUESQ_LOG_ANIM_CB=1 ROGUESQ_LOG_TMEM_ZERO=1 \
       ROGUESQ_LOG_ANIM_TEX_STREAM=1 ROGUESQ_LOG_HANGAR_ENTRY=1 \
       ROGUESQ_LOG_COMPOSE_NPC=1 ROGUESQ_LOG_DLENTRY=1 \
       ROGUESQ_LOG_ANIM_KEYFRAME_GUARD=1 ROGUESQ_LOG_COMPOSE_NPC_GUARD=1 \
       ROGUESQ_LOG_PROJECT_MODEL_BOUNDS_GUARD=1 \
       ROGUESQ_LOG_MUSYX_DMA_CALL=1 \
       ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_RING=1 ROGUESQ_LOG_DMA_CALLER=1 \
       ROGUESQ_LOG_THREAD_RESUME=0 \
       PROBE_MODE=start_only HOLD_S=30 zsh \
       /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/s73_post_a_scene/run_mission_keys.sh s102_<name> 0 12
   ```
   Run in the **background**; wait for the PID the wrapper script prints
   (or `pgrep -fl 'RogueSquadron64Recomp$'`, never `pgrep -f
   "build/RogueSquadron64Recomp"` — s100's lesson, the binary's argv0 has
   no `build/` prefix) to exit before reading `run.log`.

## Outcomes

1. **Confirmed wrong-offset/wrong-field bug, guard/fix lands, `do_rom_read`
   does not recur (or recurs with a now-sane `devAddr`)** — this would be
   the first real fix (not just a defensive guard) to the do_rom_read
   family; M3's DMA-adjacent blocker may be resolved. Re-run the soak once
   more to confirm before declaring it closed (two soaks, not one, given
   how many sessions this bug has resisted).
2. **The corrupted value doesn't match any neighboring field** — the bug
   is more subtle than a wrong-offset read (maybe a genuine cross-thread
   race on this specific global, given `musyxSynthFrame` runs on the VI
   retrace thread while other threads also touch shared state). Write up
   what was ruled out and what the remaining hypothesis is; do not force
   a guess-and-check fix without evidence.
3. **A hangar-tick-family crash (9th, 10th, 13th-15th, 17th — see
   CURRENT-TRUTH's crash catalog under item 1) preempts the soak before
   it reaches the ~140s window again** — if it's a recurrence, that's a
   useful data point (the 11th/12th/16th guards may not be sufficient
   alone); if it's an 18th+ new class, catalog it and pick whichever of
   the still-unguarded classes (14th `reserveAndEmitDLEntry`, 17th
   `updateHangarBayScene`) to guard next, per item 0's own guidance,
   rather than re-attempting this exact repro a 2nd time in the same
   session (rule 8).

## Do not

- Do not re-soak `activateAnimationKeyframe`, `composeNpcOrientationMatrix`,
  or `projectModelBoundsToScreen` — all three guards are landed and
  validated (clean negative controls, s99-s101). Leave their
  `ROGUESQ_LOG_*_GUARD` flags armed in every soak going forward but treat
  them as closed.
- Do not re-run the plain "blind DMA-caller repro with no source read"
  — that question is closed (s101). Any future soak toward this bug
  should carry the new `ROGUESQ_LOG_MUSYX_DMA_CALL` instrument, not just
  `ROGUESQ_LOG_DMA_CALLER`.
- Do not cite `ra=0x00000000` as corruption evidence (refuted s92,
  reconfirmed every session since).
- Do not re-grep for `submitDmaRequestBatch(rdram`, ring literal
  constants, or `LOOKUP_FUNC(` call-site counts (done, stable, s93-s95).
- Do not assume `musyxSynthFrame` is part of the "never-called" MusyX RSP
  audio ucode M5 describes — it appears to be a distinct, actively-running
  HLE/native audio-tick function reached via `viRetraceHandlerThread`;
  that relationship to M5's audio ucode is unconfirmed, don't build on it
  either way without checking.
- Do not compare a raw `ctx->rN` (`gpr`/`uint64_t`) value against 32-bit
  literal bounds in any new guard — always truncate through `U32()` first.
- Do not trust a `fixup_game_funcs.py` "patched xN" report without
  checking which file(s) it patched.
- `N64Recomp/fixup_game_funcs.py` is untracked in N64Recomp's own git,
  by design — do not attempt to commit it there; the durable record lives
  in `PORTING-STATE.md`/`CURRENT-TRUTH.md` in this repo.
