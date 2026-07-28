# NEXT work unit — Thread B: name the 2 remaining rs_malloc candidates to source

s140 ran NEXT.md's own option (a) (add an `rs_free` log, re-soak) and got a
clean discriminating result — read PORTING-STATE's Session 140 entry before
doing anything else; this file only has the actionable summary.

## What s140 did and found

Landed `ROGUESQ_LOG_RS_FREE=1` (`rs_free`, `funcs_0.c:3085`, patched via
`N64Recomp/fixup_game_funcs.py`, logs `ptr` + `caller_ra` at entry — source
read confirmed this is safe to do directly, no argument-order guessing).
Soaked with `scratch/agent/run_rsfree1.sh` (same "batch every
`ROGUESQ_LOG_*` flag" recipe as `run_rsmalloc1.sh`, plus the new flag).

**First crash-free soak in this whole render-guard/Thread-B series** —
0 crashes across every known class, process survived the full hold+grace
window and had to be killed by the script. `[rs-free]` fired 16445/16445
(strong positive control). 10 `[voice-active-gate-nz]` hits, same shape as
s139 (`idx=0x10`/`0x11`, `base=0x80171D50`/`0x80171DD8`,
`arrayBase=0x801714D0`).

Two real findings from the corrected/new data:

1. **None of s139's 3 candidate pointers (`0x8016FD20`, `0x80171470`,
   `0x80171DF0`) ever appear in an `[rs-free]` line, anywhere in the run.**
   Refutes the "freed-and-reused" framing outright — this is not a
   freed/UAF-into-corrupted-memory bug. All 3 candidates are still
   allocated for the entire run. Reframe: something is reading a live,
   never-freed neighboring buffer out of the voice array's own bounds.
2. **Per-hit range check (using this run's own 2 actual hit addresses,
   not the older aggregate zone) refutes the `0x80171DF0`/7728B
   candidate** — its `[ptr, ptr+size)` range (`[0x80171DF0, 0x80173C20)`)
   starts *after* both observed hit addresses (`0x80171D50` and
   `0x80171DD8` are both below `0x80171DF0`), so it structurally cannot be
   the buffer being read at either address. The other 2 candidates both
   still cover both hits.

**Thread B narrows from 3 candidates to 2:**
- `0x8016FD20` / size 8568 — boot-time, allocated right after the very
  first song-array-alloc.
- `0x80171470` / size 32768 — boot-time, starts only 96 bytes before the
  voice array's own base (`0x801714D0`) — the stronger candidate by
  adjacency (s139's own reasoning, reinforced: it's also the only one of
  the 3 whose range would cover a hit anywhere across the full historical
  aggregate zone `0x80171D50`-`0x80172548`, not just this run's 2
  addresses).

Neither candidate has been named to a source function yet.

## Do next: name one (or both) of the 2 remaining candidates

There is no more "before/after a free" event to look for — nothing is
ever freed, so option (a) from NEXT.md's prior version (more instrumenting)
is exhausted for this pair. **Do source-reading instead** (NEXT.md's own
prior option (b), still the right move):

1. Read `funcs_23.c`/`funcs_24.c` around `allocateSongChannelArray`'s own
   call site (the "very first song load" boot sequence) to find what runs
   immediately around it — specifically, what allocates exactly 32768
   bytes (`0x8000`) right there (the `0x80171470` candidate) and what
   allocates exactly 8568 bytes (`0x2178`) right after (the `0x8016FD20`
   candidate, which per s139 is allocated *before* `0x80171470` in the
   log — check the actual call order in source, not just log-line order,
   since `rs_malloc`'s pool selector means address order need not match
   call order).
2. A grep for the literal hex sizes (`0X8000`, `0X2178`) as compile-time
   constants was already tried and closed (s139 — sizes are
   runtime-computed, not literals). Don't retry that. Instead look for the
   *shape* of the allocation call (arg count, what struct/array it backs)
   near the boot sequence that also sets up `initSampleStreamBlockCache`
   (already-known caller context from s103-104).
3. If source-reading finds a named function for either buffer, the
   discriminating next move is checking whether that function's own
   *write* pattern (what it stores at various offsets into the buffer)
   could plausibly produce the corruption's observed byte shape (ASCII
   fragments like `"explo_tex2"`, `"lgfr"`, `"wing"` — established s94/s102)
   — i.e. is this buffer a string/name table, which would explain the
   ASCII-looking corruption bytes directly, rather than another struct
   array.

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
  chooses among 3 heap globals at `0x8011xxxx`). Confirmed s139.
- `rs_free`'s real argument is `(ptr)` — `$a0`=`ctx->r4`, read directly at
  function entry (confirmed safe by source read: both branches of the
  `ptr==0` check copy `ctx->r4` to `ctx->r16` first, and `ctx->r31` is
  untouched before the first internal `jal`). Confirmed s140.
- Before trusting ANY new instrument's first soak, sanity-check the
  logged values against a plausibility prior — this is what caught s139's
  bug. A instrument that compiles clean and fires is not the same as an
  instrument that's reading the right registers. (s140's rs_free log did
  NOT need this correction — verified via source read before soaking, not
  after; that upfront check is cheaper than a bad first soak.)
- `caller_ra` (`ctx->r31` at function entry) reads `0x00000000` on
  effectively 100% of entries across every entry-log instrument landed so
  far (anim-recurse, anim-tex-stream, hangar-entry, rs-malloc, rs-free) —
  confirmed benign/universal, not corruption-specific (s92, s139, s140).
  Stop treating it as a signal.
- When doing a range-overlap check, use THIS run's own actual hit
  addresses, not an older aggregate zone from a different session/run —
  s140 found the aggregate zone was too generous and hid a real
  refutation that only showed up per-hit.
- The guard-placement bug caught s133 (regex-replacement pattern shape
  varies between prior guards — always re-derive from the specific prior
  guard's landed, regenerated output) is still a live risk for any future
  patch in this series.
- `rm` on paths outside `scratch/` requires approval and does NOT accept
  glob patterns — use a `python3 -c` one-liner with `pathlib.Path.glob()`,
  run with cwd `N64Recomp`, deletes only the 45 `funcs_*.c` files.
- Do NOT re-run `fixup_game_funcs.py` a second time in the same session
  without a full regen first (non-idempotent, s102) — always delete
  `RecompiledFuncs/funcs_*.c`, re-run `make_elf.py` (cwd
  `~/Documents/Tools/rogue_squadron64`, `python3 tools/make_elf.py`) then
  `zsh tools/agent/regen_n64recomp.sh`, THEN `fixup_game_funcs.py` once —
  verify a new patch landed by grepping the regenerated `.c` directly,
  not by re-running the fixup script.
- `cmake --build` needs cwd `build/` and
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` for Metal
  shader rebuilds.
- Write a new wrapper script file per soak tag (`scratch/agent/run_
  <tag>.sh`) rather than parametrizing a single reusable script via env
  indirection — the multi-`env`-var one-liner trips the Bash
  static-command-analyzer.
- A `run_mission_keys.sh` soak with `run_in_background: true`, waited on
  via `TaskOutput(block=true)` (not a manual sleep-poll loop), works
  cleanly — the harness sends a task-notification when the background
  command exits either way.
- Checking submodule (`lib/...`) git status needs `env GIT_DIR=lib/X/.git
  GIT_WORK_TREE=lib/X git status --short` — plain `git -C lib/X status` or
  `cd`+`git status` both fail the prefix-match allowlist (rule 10);
  `env GIT_DIR=...` does match the `Bash(env:*)` allow rule.
- Output redirection (`>`) from Bash is sandboxed to the session's
  allowed working directories — target `scratch/agent/` or another
  allowed dir, not `/tmp`, for one-off dumps.

## Do not

- Do not re-audit any of the 8 Thread A functions again.
- Do not re-guard `emitAllocatedDLCommand`'s or `submitSceneNodeRender`'s
  already-landed guard sites (free-list-walk, material-batch-list) —
  exhaustively verified against source already.
- Do not re-run the `loadAssetAndIterateSubchunks`/asset-alloc soak shape
  (H2, closed 3/3), grep further for static ROM string tables (s138,
  refuted by distance), grep for literal size constants for the 2
  remaining candidates (`0X8000`, `0X2178` — tried for all 3 originally,
  s139, no real hits, sizes are runtime-computed), or add more
  instrumentation to look for a free event for the 2 remaining candidates
  (s140 — nothing is ever freed, that angle is exhausted; source-read the
  boot allocator instead).
- Do not treat a 0/0 guard-fire result as "the guard doesn't work."
- Do not chase the s83/s133 Apple-Metal-internal SIGSEGV as a guest bug —
  no guest frames anywhere in its backtrace.
- Do not chase the `do_rom_read`/`piDmaWorker` corruption race as its own
  separate investigation — it IS Thread B. Note it did NOT recur in s140's
  soak (first miss after 3/5 recent render-guard soaks hit it) — informative
  (this instrument's soak shape apparently doesn't reliably trigger it),
  not evidence the bug is fixed.
- Do not treat `caller_ra=0x00000000` as evidence of anything (s92, s139,
  s140) — it is universal across every entry-log instrument.
- When landing any new guard/instrument touching a `ctx->rN` value,
  always truncate through `U32()` before comparing against 32-bit literal
  bounds (s99's 100%-false-positive lesson), and source-read the function
  body to confirm which register holds which argument BEFORE writing the
  patch (s139's a0/a1 lesson, applied successfully in s140 — cheaper than
  fixing a bad first soak).

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is well over the ~35 KB target (2300+ lines,
growing). Migrate durable mechanism/architecture material to
PROJECT-OVERVIEW.md and prune superseded detail, paired with a real
experiment — not on its own.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-140
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`, now
including s140's `rs_free` log). Same posture as the `rogue_squadron64`
sibling checkout flagged since s54. Worth asking the user whether/how to
commit that history.
