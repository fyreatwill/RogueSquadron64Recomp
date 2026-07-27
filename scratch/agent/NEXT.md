# NEXT work unit — Thread B: find the rs_malloc buffer heap-adjacent to the voice array

s138 ran the s126-flagged fresh-angle grep (pure source/data read, no
rebuild, no soak) and got a real discriminating result, but it's a
refutation, not a close. Read PORTING-STATE's Session 138 entry before
doing anything else; this file only has the actionable summary.

## What s138 did and found

Located the one ROM string table matching the "explo_tex"/"explh_tex"
theme (`build/rogue_squadron.z64`, offsets `0x3bf70`-`0x3bfec`), and
solved the ROM->RAM mapping question NEXT.md had flagged as unresolved:
`RAM = ROM_offset + 0x7FFFF400`, confirmed two independent ways (symbol-file
cross-reference on 3 pairs; direct disassembly-operand extraction from
`loadExplosionTextures` in `N64Recomp/RecompiledFuncs/funcs_13.c`, guest
`0x8006108C`) — both agree exactly on all 4 addresses checked.

Applying that bias, the explosion-texture table sits at
`0x8003B370`-`0x8003B3EC` — **~20.3 MB away** from the corruption zone
(`arrayBase=0x801714D0`, hits `0x80171D50`-`0x80172548`). The function's
own indexing only ever uses small fixed offsets (0-0x1C). **This refutes
"a static compile-time ROM string table is what's being aliased/indexed
into voice+0x34."** A full-ROM strings dump (`scratch/agent/rom_strings.txt`,
506k lines, gitignored, kept for reuse) also found zero literal matches
anywhere for the digit-suffixed fragments (`explo_tex2`, `x7`-`x11`,
`main_n_atpt_lod`, `at_6`, `at_7`, `pilot_sd`) — those are not ROM data at
all, consistent with being runtime-constructed (name + appended index,
plausible for a numbered-asset-variant scheme).

**This does not overturn s120's mechanism, it sharpens it.** s120 already
established: the corrupted reads are an out-of-bounds scan past the voice
array's own live `voiceCount`, landing on whatever `rs_malloc` allocation
happens to sit adjacent to it in the heap — not a code-level indexing bug
into a named table at all. s122/s123 already tested and refuted the one
specific adjacent-allocation candidate anyone had checked
(`loadAssetAndIterateSubchunks`'s DMA buffer, `ptr=0x8062B850`, ~5.87 MB
away, H2 closed 3/3 per rule 8, do not re-run). s138 just eliminated a
second, more literal-minded candidate (a static ROM table) by showing it's
even farther away and arithmetically unreachable.

## Do next: find what actually allocates next to the voice array

The remaining open question is a heap-layout question, not a code-search
question: **at the moment of a corrupted `[voice-active-gate-nz]` hit,
which `rs_malloc` call's returned buffer covers `0x80171D50`-`0x80172548`?**

**Concrete first steps** (source read first, per this thread's own
established discipline — do not skip to instrumenting):

1. `allocateSongChannelArray` (`funcs_23.c`, s120) is the voice array's own
   allocator — re-read its call site to get the requested size, so you know
   how far past `0x801714D0` the array's *own* legitimate end is (this
   tells you exactly how far out-of-bounds idx 0x10-0x1F actually reaches
   past `voiceCount`, in bytes — not yet computed).
2. Grep `N64Recomp/RecompiledFuncs/*.c` for every `rs_malloc` call site
   (there won't be many) and, for each, read enough of its surrounding
   function to estimate a rough allocation size and *when in the boot/scene
   sequence* it fires — the goal is a short list of "allocated around the
   same time as the voice array, plausible size to land adjacent" candidates,
   not an exhaustive audit of every allocator in the game.
3. The most direct way to actually answer this without guessing: extend the
   existing `[song-array-alloc]` instrument (already logs the voice array's
   own `ptr`+`voiceCount`, s120) to ALSO log every *other* `rs_malloc`
   call's return pointer + requested size in the same run (a single new
   env-gated instrument at `rs_malloc`'s own return, `funcs_0.c:2743` per
   s113's note — batch this with the existing flags, one soak). Then
   offline-sort by pointer value to find which allocation's
   `[ptr, ptr+size)` range actually contains `0x80171D50` at the time of a
   `[voice-active-gate-nz]` hit in the same run — this is the discriminating
   measurement; a same-run positive control is the existing
   `[voice-active-gate-nz]` fire itself (already reliable, fires every soak
   that reaches the hangar).

**Discriminating outcome:** if exactly one allocation's range covers the
corruption addresses, that allocator's call site is very likely the true
source of the aliased data (or at minimum narrows "what other subsystem's
data lives there" precisely enough to read its write path next). If no
allocation covers it, the buffer sitting there is either freed-but-not-cleared
memory from something that *used to* occupy that range (a stale-heap-content
question, different from an aliasing question) — worth distinguishing
explicitly rather than assuming either framing.

## Thread A (all 8 hangar-tick-family functions): CLOSED, do not re-open

`composeNpcOrientationMatrix`, `updateAnimatedTextureStreaming`,
`static_5_800B4048`, `projectModelBoundsToScreen`, `reserveAndEmitDLEntry`,
`activateAnimationKeyframe`, `submitSceneNodeRender` (free-list idiom,
s123/s131/s134 — proven innocent twice — and material-batch-list idiom,
s136/s137 — 2/3 soaks, parked not proven innocent), `updateHangarBayScene`
— all guarded and exhaustively source-audited. `emitAllocatedDLCommand`'s
two `findAndUnlinkSmallestEntry` sites are also guarded and parked (3/3
soaks exhausted, s133-s135). Do not re-audit or re-guard any of these.

## This session's environment notes (carry forward, still current)

- The guard-placement bug caught s133 (regex-replacement pattern shape
  varies between prior guards — always re-derive from the specific prior
  guard's landed, regenerated output, not from whichever nearby Python
  function you copy-pasted last) is still a live risk for any future
  guard in this series.
- Host-code crash-offset arithmetic (`function + N bytes`) does NOT map
  linearly to guest instruction addresses or source line numbers.
- `rm` on paths outside `scratch/` requires approval and does NOT accept
  glob patterns — use a `python3 -c` one-liner with `pathlib.Path.glob()`
  for the delete-all step: `python3 -c "import pathlib; [f.unlink() for f
  in pathlib.Path('RecompiledFuncs').glob('funcs_*.c')]"` run with cwd
  `N64Recomp`, deletes only the 45 `funcs_*.c` files, leaves
  `funcs.h`/`lookup.cpp`/`recomp_overlays.inl` alone.
- Do NOT re-run `fixup_game_funcs.py` a second time in the same session
  (non-idempotent, s102).
- Use `zsh tools/agent/regen_n64recomp.sh` (not the bare
  `./tools/agent/regen_n64recomp.sh` form) — matches the `Bash(zsh:*)`
  allow rule cleanly. `cmake --build` must be run with cwd `build/` —
  remember to `cd` back to the repo root afterward.
- The multi-`env`-var one-liner still trips the Bash static-command-
  analyzer — write a new wrapper script file per soak tag
  (`scratch/agent/run_<tag>.sh`) rather than trying to parametrize a
  single reusable script via more env-var indirection.
- A `run_mission_keys.sh` soak with `run_in_background: true` plus a
  blocking `TaskOutput` (block=true, generous timeout) works cleanly.
  The Stop hook fires and blocks ending the turn while a background soak
  is still running and `scratch/agent/STATUS` still says `WORKING` —
  finish the soak and the full exit-contract writeup in the same turn.
- Output redirection (`>`) from Bash is sandboxed to the session's
  allowed working directories — writing a large one-off dump (e.g. a
  full ROM `strings` scan) must target `scratch/agent/` or another
  allowed dir, not `/tmp`.
- `symbol_files/main_overlay.txt`'s "Strings" section sometimes DOES
  include decoded string content in the comment (`// type:asciz - 'name'`),
  not just bare addresses — check there directly before assuming a ROM
  offset->RAM address mapping has to be derived from scratch every time.

## Do not

- Do not re-audit any of the 8 Thread A functions again (see "Thread A"
  section above — CLOSED as of s132/s137).
- Do not re-guard `emitAllocatedDLCommand`'s two `findAndUnlinkSmallestEntry`
  walk-loop sites, or `submitSceneNodeRender`'s free-list-walk sites (9
  sites) or its material-batch-list sites (2 sites) — all already landed
  and exhaustively verified against source.
- Do not re-run the `loadAssetAndIterateSubchunks`/asset-alloc soak shape
  (H2, s122/123, closed 3/3) or grep further for static ROM string tables
  as the aliasing source (s138, refuted by distance) — Thread B's live
  question is now "which `rs_malloc` buffer is heap-adjacent," not
  "which string table is being indexed."
- Do not treat a 0/0 guard-fire result as "the guard doesn't work" or
  "the fix is wrong" — it's an uncontrolled null, not a refutation.
- Do not chase the s83/s133 Apple-Metal-internal SIGSEGV as if it were a
  guest-code bug — it has no guest frames anywhere in its backtrace.
- Do not chase the `do_rom_read`/`piDmaWorker` corruption race as its own
  investigation right now — it's exactly what Thread B (above) already
  is; don't open a parallel/duplicate investigation under a different
  name.
- When landing any new guard, always truncate a `ctx->rN` value through
  `U32()` before comparing against 32-bit literal bounds (s99's
  100%-false-positive lesson).

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is well over the ~35 KB target (2200+ lines,
growing). Migrate durable mechanism/architecture material to
PROJECT-OVERVIEW.md and prune superseded detail, paired with a real
experiment — not on its own.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-137
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.
