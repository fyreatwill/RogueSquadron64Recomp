# NEXT work unit — M3: source-read + guard the 17th hangar-tick crash class, `updateHangarBayScene` (s110)

s109 guarded the 14th class (`reserveAndEmitDLEntry`) — landed clean,
patched x1, built clean, one soak. The guard read 0/0 (clean negative
control, no positive control yet — `a0` was never bad this run). The
process still died at 73.9s, the same 73.5-73.9s window all 3 of s108's
soaks died in, but this time to a **brand-new 19th class**, not a
recurrence of anything already known. Read PORTING-STATE.md's Session 109
entry before doing anything else; this file only has the actionable
summary.

## Why this is the next work unit

CURRENT-TRUTH item 0b already named the 17th class (`updateHangarBayScene`
itself, `static_5_800AB658`, s100) as the next guard candidate once the
14th was done. It has the strongest existing characterization of any
remaining unguarded class: a confirmed real backtrace (s100), a
distinguishing feature already established (outer call chain matches the
10th class but one frame shallower, no `static_5_800B4048` frame), and — no
guard has ever needed more than one soak's worth of source-reading to
write once the crash site itself is opened up. This is strictly cheaper
than chasing either of the two brand-new single-occurrence classes below,
which don't meet the project's 2nd-recurrence bar for instrumenting yet.

## What's confirmed (do not re-derive)

- Two new single-occurrence crash classes now block reliable passage to
  the ~140s DMA window, alongside the pre-existing family:
  - **Probable 18th** (s108): SIGBUS, nearest symbol
    `heapFreeListDequeue + 12704` (`N64Recomp/RecompiledFuncs/funcs_3.c:15176`,
    same file as `reserveAndEmitDLEntry`, immediately after
    `reserveAlignedDLSpace`), same outer chain as the 14th class but no
    `reserveAndEmitDLEntry` frame in the trace.
  - **19th** (s109): RT64-internal SIGSEGV in `plume::MetalFramebuffer`'s
    constructor via `RT64::FramebufferManager::createTileCopyRecord` →
    `RT64::RenderTarget::setupColorFramebuffer`/`clearColorTarget` →
    `plume::MetalDevice::createFramebuffer` — a render-thread frame, not
    the guest hangar-tick chain the rest of the family shares. Preceded in
    the log by several `[last-drawn-skip]` wild/OOB rejections
    (`addr=0x000BCA20 w=689`, `addr=0x00000000 w=97/193`) — plausibly
    related, not confirmed.
  **Neither has recurred once — do not instrument either yet.** Just watch
  for a 2nd hit of either in any future soak (both are single-occurrence
  per the project's own convention for when instrumenting is worth a
  build-run cycle).
- The 17th class itself (`static_5_800AB658`/`updateHangarBayScene`, s100):
  fault resolves directly inside the function's own body (confirmed
  distinct from the 10th class, whose innermost frame `static_5_800B4048`
  is absent from this backtrace). **Not yet source-read** — that is this
  session's first step, same as every prior guard (s99-s101, s109) did
  before writing anything.
- The reference guard shape (all four landed so far — 16th, 12th, 11th,
  14th — follow this exactly):
  1. Sanity-check the suspect pointer register with `U32(ctx->rN)` truncated
     first (a `gpr`/uint64_t sign-extends on assignment; comparing without
     truncating made an early guard fire 100% of the time, s99's own
     lesson — see `_activate_anim_keyframe_guard_patch` in
     `N64Recomp/fixup_game_funcs.py` for the exact bug and fix).
  2. Bounds: `< 0x80000000u || >= 0x80800000u` (RDRAM is 8MB, guest-mapped
     0x80000000-0x80800000).
  3. On failure: log (capped or gated by an enabled-flag pattern, following
     whichever family member is most similar), then `goto` a **real**
     epilogue label — never a bare `return;` (skips register restore,
     breaks MIPS ABI for the caller). If no existing label is reachable
     ABI-safely from the guard's insertion point (s109's situation — see
     below), insert a **new dedicated label** immediately before the real
     restore sequence via `re.subn`, anchored on that unique restore-
     sequence text, rather than reusing a label whose block does unrelated
     cleanup work (s109's own comment in `fixup_game_funcs.py` explains why
     `L_8000CE58` was unsafe to reuse for the 14th class's guard).
  4. File-scope the regex (`if p.name == "funcs_N.c"`) even when the anchor
     text looks unique — s100 found a real cross-overlay collision this
     way (`composeNpcOrientationMatrix`'s anchor also matched inside
     `hangarInitialize`, a different function in a different overlay
     sharing the same guest address range).
- **Placement subtlety from s109, applies here too**: don't assume the
  earliest point after the suspect register is assigned is safe to guard
  from. Check whether the function's own prologue has saved every register
  the target epilogue restores (`$ra` and any `$sN`) to their stack slots
  *before* the point you insert the guard — if not, jumping to a
  restore-from-stack epilogue early will load uninitialized stack bytes
  into those registers. Trace the actual save order in the disassembly
  comments (`sw $ra, ...($sp)` etc.) before picking the insertion point,
  the way s109 had to move its guard past the function's own existing
  bounds-check branch to land after the real `$ra` save.

## The work unit

1. **Source-read `updateHangarBayScene`** (`static_5_800AB658` — check
   `symbol_files/main_overlay.txt` first for a real name the way s97 found
   `composeNpcOrientationMatrix`'s; the recompiler may still emit the
   `static_5_` fallback name even if a real name is assigned, same
   "symbol assigned to a non-overlay file" shape as several M4 items).
   Find: which argument or which fixed-table-derived pointer is
   dereferenced without a range check, and where relative to function
   entry; the function's real epilogue (register restore + return),
   confirmed by reading to the function's closing brace, not assumed from
   a nearby label.
2. **Write the guard** in `N64Recomp/fixup_game_funcs.py`, following the
   reference shape above. Add a fresh env var name
   (`ROGUESQ_LOG_HANGAR_BAY_SCENE_GUARD` or similar — check it doesn't
   collide with the existing `ROGUESQ_LOG_HANGAR_ENTRY` from the 10th
   class's diagnostic, which is a different function).
3. **Regen order**: `cd ~/Documents/Tools/rogue_squadron64 && python3
   tools/make_elf.py` → `cd ~/Documents/Tools/N64Recomp && python3 -c
   "import subprocess; subprocess.run(['./build/N64Recomp',
   'rogue_squadron.toml'])"` (direct binary invocation is not allowlisted
   and prompts for approval) → `python3 fixup_game_funcs.py` → `cd
   ../RogueSquadron64Recomp && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
   cmake --build build -j 8`. **Full ELF regen, not a bare fixup re-run**
   (idempotency bug still unfixed — see Tooling note). Verify the fixup
   report shows the new guard patched exactly `x1`, in the one expected
   file only.
4. **Soak** (same repro shape, add the new guard's log flag alongside the
   existing set):
   `cd scratch/s73_post_a_scene && env ROGUESQ_LOG_MUSYX_DMA_CALL=1 ROGUESQ_LOG_FILL_RANGE_ARGS=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_LOG_DLENTRY=1 ROGUESQ_LOG_DLENTRY_GUARD=1 ROGUESQ_LOG_HANGAR_BAY_SCENE_GUARD=1 ROGUESQ_LOG_THREAD_RESUME=0 PROBE_MODE=start_only HOLD_S=30 zsh run_mission_keys.sh s110_hangarbay_guard 30 12`
   (backgrounds past the 120s foreground timeout — block on the task
   notification, don't poll).
5. **Interpret**: if the process now reaches `vi_width=640`/~140s alive (or
   at least survives past 73.9s where s108/s109's 4 soaks all died), that's
   a real improvement — re-attempt `musyx-gate1` next (item -1's countdown/
   period question, still untested against the window). If it dies before
   the window again to yet another new class, log it as the 20th and keep
   working down the list — but at that point consider whether a broader
   fix (e.g. a blanket pointer-validation wrapper at the scene-graph-
   traversal chokepoint, `submitSceneNodeRender`/`processSceneNode`, shared
   by the 14th/17th/18th/probable-new classes) would be higher-value than
   guarding classes one at a time — this has not been tried and multiple
   sessions now show new classes appearing in the same 2-3 outer functions.
   If the new guard fires (a real positive control, unlike s109's 14th-class
   guard), that closes the 17th class with full confidence — note that
   explicitly, it would be the first guard in this family to get one.

## Also flagged (s109, not this session's job)

- The 14th class's guard (`ROGUESQ_LOG_DLENTRY_GUARD`) still has no
  positive control. Leave it armed in every soak; if it ever fires, that's
  a free confirmation, don't design a soak around chasing it specifically.
- Consider (not yet attempted, raised s109): a single guard at the
  scene-graph-traversal chokepoint shared by the 14th/17th/18th/19th
  classes (`submitSceneNodeRender`/`processSceneNode`/
  `traverseSceneGraphRecursive`) might catch bad pointers before they reach
  any of the per-function leaves, cheaper than one guard per leaf. Not
  designed yet — would need to identify what's actually shared (a node
  pointer? a render-target handle?) across all four call chains first.

## Tooling note — still not fixed, still cheap

`fixup_game_funcs.py` is **not idempotent** by construction (every patch's
anchor regex matches text left unchanged after insertion). A full ELF
regen has now avoided the duplication symptom seven times in a row
(s103-s109) as a workaround. If a session touches `fixup_game_funcs.py`
again, consider actually fixing it: make each patch's anchor regex also
require a negative lookahead that the match is **not** immediately
followed by `    { // PATCH:`. Test by running the script twice in a row on
an already-regenerated tree and confirming the 2nd run reports 0/"no
changes needed" for every already-landed patch.

## Housekeeping flagged, not this session's job either

`docs/CURRENT-TRUTH.md` is now ~104 KB, roughly 3x the ~35KB target in
CLAUDE.md/ITERATION.md. This has been growing for many sessions past the
target — not caused by any single iteration, but worth a dedicated
compression work unit (migrate durable mechanism/architecture material to
PROJECT-OVERVIEW.md, prune superseded detail more aggressively) before it
grows further. Per ITERATION.md, compressing CURRENT-TRUTH does not count
as an "ADVANCED" work unit on its own — pair it with a real experiment, or
treat it as an explicit, acknowledged exception.

## Do not

- Do not re-soak the 4 already-guarded classes (16th, 12th, 11th, 14th) in
  isolation — treat them as closed pending an eventual positive control
  that arrives for free from an unrelated soak.
- Do not instrument the probable-18th or 19th classes yet — both are
  single-occurrence; wait for a 2nd hit.
- Do not use a bare `return;` in the new guard — always `goto` a real
  epilogue label that restores saved registers, per every prior guard.
- Do not compare a raw `ctx->rN` (`gpr`/uint64_t) value against 32-bit
  literal bounds without truncating through `U32()` first (s99's lesson).
- Do not insert a guard's `goto` target before confirming every register
  the target epilogue restores is already saved to its stack slot at the
  guard's insertion point (s109's lesson — see Placement subtlety above).
- Do not trust a `fixup_game_funcs.py` "patched xN" report without
  checking which file(s) it patched, and do a full ELF regen first if the
  tree may already carry prior patches.
- Do not cite `ra=0x00000000` as corruption evidence (refuted s92); do not
  re-open "random/race/stomp" framings for the `devAddr` corruption (7+
  independent lines of evidence against all three) — unrelated to this
  session's work but still a live trap in the docs.
- `N64Recomp/fixup_game_funcs.py` is untracked in N64Recomp's own git, by
  design — do not attempt to commit it there; the durable record lives in
  `PORTING-STATE.md`/`CURRENT-TRUTH.md` in this repo.
