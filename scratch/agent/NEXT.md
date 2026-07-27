# NEXT work unit — find what writes/aliases string-table data into voice+0x0 at in-bounds indices (s122)

s121 closed both the "scan runs out of bounds" and "loop-bound global
itself corrupted" branches for the `voice+0x0` mystery (direct,
sign-extension-fixed reads of `count=`/`arrayBase=` were sane, and every
observed `idx` was *inside* the live allocation, not past it). Read
PORTING-STATE.md's Session 121 entry before doing anything else; this
file only has the actionable summary.

## Where this leaves the M3 voice-corruption thread

Two independent lines of evidence (s118's widened dump, s121's
bounds-checked read) agree: the byte(s) at `voice+0x0` for real,
in-bounds voice-array slots contain recognizable ASCII string-table
fragments (`expl_tex2`, `x10`/`x11`, `explo_te`, `star_`, `atpt_load`,
`mat_6`, `xenlight`, `xckpit`, etc. — `main_overlay.txt`'s own comments
confirm these are real asset/texture names, not noise). The open
question is now squarely: **what other code writes into (or aliases)
the voice array's memory with string-table content, at legitimate
per-voice offsets, without ever touching the count/base globals?**

Competing hypotheses to discriminate between:
- (H1) **Heap reuse, not aliasing** — a texture/asset name-table buffer
  is allocated, used, and freed, and its memory is later handed back
  out as (or overlaps) the voice array's allocation from `rs_malloc`,
  without the voice array itself being zeroed on reuse. This would
  mean `voice+0x0` isn't being written by anyone *as a voice field* —
  it's stale leftover content from a completely different, already-
  freed structure that happened to share the address range.
- (H2) **Genuine aliasing** — two live pointers (the voice array and
  some name-table structure) both resolve to overlapping memory at the
  same time, meaning something is currently writing string data into
  what the voice code treats as its own array (a real corruption, not
  just stale reuse).
- (H3) **Same source as `devAddr`'s corruption** (s94-104's parked
  thread) — already weakened by s118 (0 literal byte-matches between
  same-run `devAddr` corruption and the voice-array strings), but not
  fully closed; keep as a lower-priority fallback, not the lead
  hypothesis.

## The discriminating measurement

H1 vs H2 splits cleanly on **timing**: if it's H1 (stale reuse), the
string content at `voice+0x0` should already be present *immediately
after* `allocateSongChannelArray`'s `rs_malloc` returns — before any
per-tick voice code runs — because it's inherited straight from
whatever the allocator handed back. If it's H2 (live aliasing), the
array should read clean/zeroed immediately after allocation and only
pick up string content *later*, coincident with some other subsystem's
write.

**Concrete next step**: extend the existing `_song_array_alloc_patch`
(`funcs_23.c`, `ROGUESQ_LOG_SONG_ARRAY_LIFECYCLE=1`) to dump the first
N bytes (suggest 0x88*4 = one full stride times a few slots, matching
`_voice_active_gate_patch`'s own dump width) of the freshly-`rs_malloc`d
array **immediately after allocation, before any zeroing the function
itself might do** (check the source around the `rs_malloc` call in
`allocateSongChannelArray` first — if it already memsets the buffer,
that changes where to hook). Compare against the `[voice-active-
gate-nz]` dumps already captured (s118/s121) for the same session's
addresses.

- **If the string content is already present right after `rs_malloc`
  returns (before any zeroing, or the code has no zeroing step at
  all)**: H1 confirmed — this is `rs_malloc` handing back
  previously-used, non-zeroed memory from a freed name-table
  allocation, and the "bug" (if any) is that the game code assumes
  `rs_malloc` zeroes or that voice slots get explicitly zeroed and they
  don't. Next step would be finding `rs_malloc`'s implementation
  (recompiled or LLE?) and confirming whether it zeroes memory by
  contract.
- **If the array reads clean immediately after allocation and only
  later shows string content**: H2 confirmed — something else writes
  after the fact. Next step: grep for name-table-populating functions
  (`loadExplosionTextures` per `main_overlay.txt`'s comment, or
  whatever function the string set resolves to) and check whether its
  buffer's address ever coincides with the voice array's `arrayBase`
  in the same run (log both pointers, diff).

## Do not

- Do not re-run the idx-vs-count `songlifecycle` soak shape again —
  closed, 3/3 attempts (`songlifecycle1/2/3`), s121 gave a clean
  discriminating result overturning s120's own framing. Any 4th
  attempt on this exact question would violate rule 8.
- Do not re-test the `shutdownAudioEngine`/`-0x6904`/`-0x6908` alias
  hypothesis as causal here — refuted 2/2 (`[shutdown-audio-free]`
  fired 0 times both soaks, s120). Still a real bug worth fixing
  someday, just not causal to this thread.
- Do not re-litigate hypothesis (b) (`musyxInitVoiceFromSample`
  comparison, s117-119) — closed.
- Do not write any new `MEM_W`/`MEM_HU`/`MEM_BU` call with a bare hex
  literal for a `lui`-computed base — always go through
  `(gpr)(int32_t)(0Xnnnn << 16)` or an in-scope `ctx->rN` that already
  holds a correctly sign-extended value. This exact bug cost s120 most
  of a session; `_voice_active_gate_patch` is the template to copy.
- When comparing two independently-logged instruments' values, do
  **not** infer temporal ordering from raw log-file line order across
  different call sites/threads unless they share an explicit sequence
  number — s121 showed this produces false "the value was already X
  before it was written" artifacts. If cross-instrument timing matters,
  add a shared monotonic counter or timestamp field to both patches
  before drawing conclusions from proximity.

## Regen reminder (delete-first is mandatory; audit every run — s121
confirmed the duplication bug is intermittent, not fixed)

1. Delete all existing output first (do NOT skip this):
   ```
   python3 -c "
   from pathlib import Path
   import os
   base = Path('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs')
   for f in base.glob('funcs_*.c'): os.remove(f)
   "
   ```
2. `python3 <rogue_squadron64>/tools/make_elf.py` (absolute path, no `cd`)
3. `zsh tools/agent/regen_n64recomp.sh` (wraps
   `cd .../N64Recomp && ./build/N64Recomp rogue_squadron.toml` as a
   single allowlisted command)
4. `python3 /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   — **read the full report, not just grep for your own patch** —
   confirm every line's `x{n}` matches its expected/intentional
   multiplicity (audio gate `x3`, musyxKeyOnVoice div-traps `x8`,
   everything else `x1`).
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8`
   — grep for `error:` explicitly; a clean exit does not guarantee no
   duplicate-but-non-erroring patches (see item 0 in CURRENT-TRUTH).
6. Soak via `env <FLAGS> PROBE_MODE=start_only HOLD_S=30 zsh
   scratch/s73_post_a_scene/run_mission_keys.sh <tag> 5 8`.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is over the ~35 KB target. Migrate durable
mechanism/architecture material to PROJECT-OVERVIEW.md and prune
superseded detail, paired with a real experiment — not on its own.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git
checkout, not a `lib/` submodule, with uncommitted changes across
s90-121 (`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`).
Same posture as the `rogue_squadron64` sibling checkout flagged since
s54. Worth asking the user whether/how to commit that history.
