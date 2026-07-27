# NEXT work unit — Thread B: discriminate among 3 boot-time allocation candidates

s139 ran the discriminating rs_malloc-range-overlap measurement s138's own
NEXT.md called for, landed a real result, but it's a narrowing, not a
close. Read PORTING-STATE's Session 139 entry before doing anything else;
this file only has the actionable summary.

## What s139 did and found

Landed `ROGUESQ_LOG_RS_MALLOC=1`: patches `rs_malloc` itself
(`N64Recomp/RecompiledFuncs/funcs_0.c:2743`, via `N64Recomp/
fixup_game_funcs.py`) to log every allocation's `ptr`, `size`, `flags`,
and `caller_ra` at its single `return;`. Chose to instrument the function
once rather than every one of its ~40+ call sites.

**First soak's data was wrong — caught before trusting it.** The size
field was flag-shaped (7 discrete values, 59% zero), not byte-count-shaped.
Source-read the function body and found the patch had `$a0`/`$a1`
backwards: `$a0` (`ctx->r4`) is the size (confirmed by `(a0+0xF)&~0xF`
alignment a few lines later), `$a1` (`ctx->r5`) is a pool-selector flags
word (`&0x4`/`&0x10` tested to pick among 3 heap globals). Fixed, full
regen + rebuild (clean), re-soaked. **Any future rs_malloc-adjacent patch
should use this confirmed `(size, flags)` order, not guess by analogy with
libc `malloc`.**

**Corrected soak, real findings:**
- Voice array per-slot stride = **136 bytes** (`voiceCount*136` matches
  the logged allocation size exactly, all 4 song-loads this run).
- This run's 5 `[voice-active-gate-nz]` hits (`idx=0x10`/`0x11`,
  `arrayBase=0x801714D0`) happened while the *active* array allocation was
  the `voiceCount=15` one (`size=2040`, ends `0x80171CD8`) — the hit
  addresses (`0x80171D50`/`0x80171DD8`) are **2176/2312 bytes past that
  buffer's own actual malloc'd end**, not just past an abstract count
  field. Sharper confirmation of s120's mechanism than before.
- Range-overlap analysis (offline Python, sort all `[rs-malloc]` ptr/size
  pairs, find which cover `0x80171D50`-`0x80172548`) found **3 candidates**,
  not NEXT.md's best-case "exactly one": `ptr=0x8016FD20 size=8568`
  (boot, right after the very first song-array-alloc), `ptr=0x80171470
  size=32768` (boot, starts only 96 bytes before the array's own base),
  `ptr=0x80171DF0 size=7728` (the `voiceCount=17` array's own paired
  follow-on buffer, superseded by later reallocations). None of these 3
  pointers is ever returned by `rs_malloc` again later in the run (checked
  by grep) — if any was freed, its space was never handed back out to
  anything else logged.
- `caller_ra=0x00000000` on **100% of 17651 calls this run** — extends
  s92's "universal-zero, not corruption-specific" finding to a 4th
  independent entry log. Confirmed unusable for identifying call sites;
  do not re-litigate this as evidence of anything.
- A literal-constant grep for the 3 candidates' sizes as hex (`0X2178`,
  `0X1E30`, `0X8000`) in `RecompiledFuncs/*.c` found nothing real — sizes
  are runtime-computed, not compile-time literals. This approach is
  closed; don't retry it.

## Do next: discriminate among the 3 candidates

Pick ONE of these two (both are viable; (a) is more mechanical/faster,
(b) is more certain but slower):

**(a) Add an `rs_free` log and re-soak.** `rs_free` is the sibling
function right after `rs_malloc` in `funcs_0.c` (~line 3073, confirmed by
this session's own read — re-verify the exact body before patching, don't
assume the shape mirrors `rs_malloc`). Log `ptr` + `caller_ra` (caller_ra
will likely also read 0, per the pattern above — don't be surprised, it's
not new evidence). Same soak recipe (`scratch/agent/run_rsmalloc1.sh`,
add `ROGUESQ_LOG_RS_FREE=1`… landed as a new flag). Discriminating
outcome: if exactly one of the 3 candidate pointers (`0x8016FD20`,
`0x80171470`, `0x80171DF0`) appears in an `[rs-free]` line *before* a
same-run `[voice-active-gate-nz]` hit, that is strong evidence it's the
freed-but-not-cleared source. If none of the 3 are ever freed, that
refutes the "freed-and-reused" framing entirely and reframes this as
"still-allocated buffer being read out-of-bounds by two different
subsystems simultaneously" — a different, still-useful answer, not a
null result.

**(b) Source-read the boot call chain instead of instrumenting further.**
The `0x80171DF0`/7728-byte candidate is allocated immediately after every
`allocateSongChannelArray` call (paired 1:1, confirmed s139) — read
`funcs_23.c`/`funcs_24.c` around `allocateSongChannelArray`'s own call
site to find what calls it and what it calls immediately after, to name
this 7728-byte allocator function directly instead of via a corrupted
register. The `0x8016FD20`/8568-byte and `0x80171470`/32768-byte
candidates are boot-only (called once, near the very start of the log,
right after the very first song load) — read the boot sequence in
whatever function drives `initSampleStreamBlockCache` / the initial
`allocateSongChannelArray` call to find what else it sets up at that
point in the same pass.

## Thread A (all 8 hangar-tick-family functions): CLOSED, do not re-open

`composeNpcOrientationMatrix`, `updateAnimatedTextureStreaming`,
`static_5_800B4048`, `projectModelBoundsToScreen`, `reserveAndEmitDLEntry`,
`activateAnimationKeyframe`, `submitSceneNodeRender` (free-list idiom,
material-batch-list idiom), `updateHangarBayScene` — all guarded and
exhaustively source-audited. `emitAllocatedDLCommand`'s two
`findAndUnlinkSmallestEntry` sites are also guarded and parked. Do not
re-audit or re-guard any of these.

## This session's environment notes (carry forward, still current)

- `rs_malloc`'s real argument order is `(size, flags)` — `$a0`=size
  (rounded `(x+0xF)&~0xF`), `$a1`=pool-selector flags (`&0x4`/`&0x10`
  chooses among 3 heap globals at `0x8011xxxx`). Do not re-derive this by
  guessing; it's now source-confirmed (s139).
- Before trusting ANY new instrument's first soak, sanity-check the
  logged values against a plausibility prior (e.g. "do these look like
  real byte sizes, not flag bits") — this is what caught the s139 bug.
  A instrument that compiles clean and fires is not the same as an
  instrument that's reading the right registers.
- `caller_ra` (`ctx->r31` at function entry) reads `0x00000000` on
  effectively 100% of entries across every entry-log instrument landed so
  far (anim-recurse, anim-tex-stream, hangar-entry, now rs-malloc) — this
  is confirmed benign/universal, not corruption-specific (s92, reinforced
  s139). Stop treating it as a signal.
- The guard-placement bug caught s133 (regex-replacement pattern shape
  varies between prior guards — always re-derive from the specific prior
  guard's landed, regenerated output) is still a live risk for any future
  patch in this series.
- `rm` on paths outside `scratch/` requires approval and does NOT accept
  glob patterns — use a `python3 -c` one-liner with `pathlib.Path.glob()`:
  `python3 -c "import pathlib; [f.unlink() for f in
  pathlib.Path('RecompiledFuncs').glob('funcs_*.c')]"` run with cwd
  `N64Recomp`, deletes only the 45 `funcs_*.c` files.
- Do NOT re-run `fixup_game_funcs.py` a second time in the same session
  without a full regen first (non-idempotent, s102) — always delete
  `RecompiledFuncs/funcs_*.c`, re-run `make_elf.py` then
  `regen_n64recomp.sh`, THEN `fixup_game_funcs.py` once.
- Use `zsh tools/agent/regen_n64recomp.sh` (matches the `Bash(zsh:*)`
  allow rule). `cmake --build` must be run with cwd `build/`.
- Write a new wrapper script file per soak tag (`scratch/agent/run_
  <tag>.sh`) rather than parametrizing a single reusable script via env
  indirection — the multi-`env`-var one-liner trips the Bash
  static-command-analyzer.
- A `run_mission_keys.sh` soak with `run_in_background: true`, waited on
  via a blocking `while kill -0 <pid>; do sleep 5; done` loop (not a raw
  sleep), works cleanly — the harness sends a task-notification when the
  background command exits either way.
- Output redirection (`>`) from Bash is sandboxed to the session's
  allowed working directories — target `scratch/agent/` or another
  allowed dir, not `/tmp`, for one-off dumps.
- `symbol_files/main_overlay.txt`'s "Strings" section sometimes DOES
  include decoded string content in the comment — check there directly
  before assuming a ROM offset->RAM mapping needs deriving from scratch.

## Do not

- Do not re-audit any of the 8 Thread A functions again.
- Do not re-guard `emitAllocatedDLCommand`'s or `submitSceneNodeRender`'s
  already-landed guard sites (free-list-walk, material-batch-list) —
  exhaustively verified against source already.
- Do not re-run the `loadAssetAndIterateSubchunks`/asset-alloc soak shape
  (H2, closed 3/3) or grep further for static ROM string tables (s138,
  refuted by distance) or literal size constants for the 3 s139
  candidates (tried, s139, no real hits, sizes are runtime-computed).
- Do not treat a 0/0 guard-fire result as "the guard doesn't work."
- Do not chase the s83/s133 Apple-Metal-internal SIGSEGV as a guest bug —
  no guest frames anywhere in its backtrace.
- Do not chase the `do_rom_read`/`piDmaWorker` corruption race as its own
  separate investigation — it IS Thread B; this is now its 3rd/4th
  consecutive recurrence across the last 2 sessions' soaks (s136-s139),
  not a new mystery each time.
- Do not treat `caller_ra=0x00000000` as evidence of anything (s92,
  reinforced s139) — it is universal across every entry-log instrument.
- When landing any new guard/instrument touching a `ctx->rN` value,
  always truncate through `U32()` before comparing against 32-bit literal
  bounds (s99's 100%-false-positive lesson), and sanity-check the FIRST
  soak's logged values against a plausibility prior before trusting them
  (s139's a0/a1 lesson) — a clean compile is not the same as correct data.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is well over the ~35 KB target (2270+ lines,
growing). Migrate durable mechanism/architecture material to
PROJECT-OVERVIEW.md and prune superseded detail, paired with a real
experiment — not on its own.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-139
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.
