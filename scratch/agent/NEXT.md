# NEXT work unit — M3: pin down the `queueGPUUploadTMEM` zero-size assert (next-steps item 1)

s89 ran the s88 soak shape twice more (`animcb2`, `animcb3`). Neither
reproduced the s87 `advancePlayerAnimationPhase` SIGBUS — that's 3
non-recurrences since s88 landed the correct instrument, so per
ITERATION.md rule 8 that specific hypothesis is now **parked** (see
CURRENT-TRUTH next-steps item 4). Do not spend this iteration chasing
it further.

Instead, both soaks crashed on other things. `animcb2` (signal 6,
Abort) gave the **first-ever full backtrace** for the s86
`queueGPUUploadTMEM` zero-size assert:

```
Assertion failed: (!decodeTMEM || ((width > 0) && (height > 0))),
function queueGPUUploadTMEM, file rt64_texture_cache.cpp, line 1285.
```

Call path: `State::fullSyncFramebufferPairTiles` → `uploadTile` lambda
(`rt64_state.cpp:1208-1330`) → `TextureManager::uploadTexture`
(`rt64_state.cpp:1329`) → `queueGPUUploadTMEM`
(`rt64_rdp_tmem.cpp:54-93` → `rt64_texture_cache.cpp:1285`).

The run also logged 25 `[rt64] loadDrawState: copy-mode draw with
undefined tile N, marking invalid` lines (`rt64_state.cpp:550`,
including tile 7 repeatedly, right up to two occurrences immediately
before the crash) — **confirmed a red herring, not the cause**: that
code path already sets `callTile.valid = false` for the tile and the
`uploadTile` lambda returns immediately via `if (!callTile.valid)
return;` (`rt64_state.cpp:1210`) before `uploadTexture` is ever called.
Do not re-chase "undefined tile" as the mechanism.

The zero width/height must come from a **valid** callTile passing
through the *same* call site. `rt64_rdp_tmem.cpp:54` (`TextureManager::
uploadTexture`) already has a dormant conditional log for exactly this
case, added s87:

```cpp
if ((width == 0 || height == 0) && std::getenv("ROGUESQ_LOG_TMEM_ZERO")) {
    fprintf(stderr, "[tmem-zero-upload] w=%u h=%u fmt=%u siz=%u line=%u "
        "tmem=%u pal=%u cms=%u cmt=%u masks=%u maskt=%u shifts=%u "
        "shiftt=%u uls=%u ult=%u lrs=%u lrt=%u tlut=0x%X\n", ...);
}
```

It has now gone **0/0 across 3 soaks** regardless of whether the flag
was armed (s87: armed, didn't fire because the soak died earlier to a
different crash; `animcb2`: not armed, hit the assert directly;
`animcb3`: armed, but the soak crashed on the *new* 9th class — see
below — before hitting this assert again). The assert and the logging
flag have never yet coincided in the same run.

## Competing hypotheses

1. **Legitimate degenerate LOADTILE.** The game occasionally issues a
   real, valid (non-corrupted) tile descriptor whose computed sample
   dimensions are genuinely 0 — e.g. `lrs<=uls` or `lrt<=ult` (an
   empty-rect load) reaching this path in a way the earlier
   `sampleWidth`/`sampleHeight` computation in `rt64_state.cpp` (lines
   ~589-596, `std::min(tileWidth, maskWidth)` with `tileWidth`/`maskWidth`
   both `std::max(...,1)`-floored) doesn't fully prevent for this
   particular call path. If so, this is a real (if narrow) engine gap —
   fix is a defensive `std::max(width,1)`/skip-if-zero at the call site
   or inside `queueGPUUploadTMEM`, not a corruption story.
2. **Same shared-corruption-race family as s85's `do_rom_read` and
   s89's `updateAnimatedTextureStreaming`.** A register/struct field
   feeding into `callTile.sampleWidth`/`sampleHeight` gets corrupted
   upstream (same unproven "something corrupts a register or nearby
   memory intermittently" hypothesis raised s85, now with 3 candidate
   sites). If so, the logged `LoadTile` fields will look implausible for
   any real N64 tile descriptor (e.g. wildly out-of-range `uls`/`lrs`),
   not just "zero-sized."

The `[tmem-zero-upload]` log (once it actually fires) discriminates
these directly per its own code comment: sane-looking fields (e.g.
`lrs<=uls`) → hypothesis 1; fields outside any real tile descriptor's
range → hypothesis 2.

## Command

Keep `ROGUESQ_LOG_TMEM_ZERO=1` armed (cheap, no-op unless width/height
is actually 0) on every soak until it coincides with the assert firing:

```
env ROGUESQ_LOG_ANIM_CB=1 ROGUESQ_LOG_TMEM_ZERO=1 PROBE_MODE=start_only HOLD_S=30 zsh \
  scratch/s73_post_a_scene/run_mission_keys.sh animcb4 0 12
```

(Reuses the existing build — no regen needed. `ROGUESQ_LOG_ANIM_CB=1`
is harmless to leave on; if the parked anim-recursion bug happens to
recur anyway, the data is still worth reading per item 4 below.)

## Discriminating measurement

1. `grep -n CRASH scratch/s73_post_a_scene/animcb4/run.log` — find the
   crash (if any) and its signal number.
2. `grep -n tmem-zero-upload scratch/s73_post_a_scene/animcb4/run.log`
   — if this fires **and** a `queueGPUUploadTMEM` assert crash follows
   shortly after, read the logged fields per the hypotheses above.
3. If this soak crashes on something else entirely (as the last two
   did), read that crash's backtrace fresh — do not assume it is one of
   the 9 known classes without checking function names against
   CURRENT-TRUTH's list.
4. If `[anim-recurse]` happens to show `sp` in the run leading up to
   *any* crash this soak, note whether it stays in the known 6-value/
   312-byte band or moves — purely as a bonus data point for the parked
   item 4, not the primary target this iteration.

## Do not

- Do not re-litigate whether "undefined tile" logging causes the
  assert — ruled out at the source level this session (`rt64_state.cpp:
  1210` already guards it).
- Do not spend this iteration chasing the `advancePlayerAnimationPhase`
  SIGBUS (parked, item 4) — 3 non-recurrences is enough per rule 8.
- If this soak's crash is the TMEM-zero assert again but the log still
  doesn't fire, double check `std::getenv("ROGUESQ_LOG_TMEM_ZERO")` is
  actually exported (the `env` prefix workaround, CLAUDE.md rule 10 /
  ITERATION.md rule 10 — a bare `VAR=1 zsh ...` is silently denied by
  the settings.json prefix match, not silently unset, so a missing log
  line could mean "didn't fire" or "command was denied": check the
  soak actually produced output at all before concluding null).
- Budget: this is iteration 1 of a fresh ITERATION.md rule-8 count for
  the TMEM-zero-assert hypothesis family (0 prior soaks had both the
  assert and the flag co-occur). Up to 3 attempts before reassessing.

## Secondary work unit if the above doesn't crash this class

Add an entry-log instrument to `updateAnimatedTextureStreaming`
(`N64Recomp/RecompiledFuncs/funcs_11.c:13665`, patch via
`N64Recomp/fixup_game_funcs.py` following the exact `_anim_cb_patch`
pattern already used for `ROGUESQ_LOG_ANIM_CB`) logging `ctx->r4` (a0,
the streaming-entry pointer) at entry. This targets next-steps item 2 —
characterizing the 9th crash class (SIGBUS via an unchecked `MEM_W`
deref off `ctx->r16`/a0, `recomp.h:95`). Read the generated C back
before building (per the s88 lesson: a mangled patch compiled fine and
only a source read caught it).
