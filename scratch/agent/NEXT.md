# NEXT work unit — Thread B: instrument the unchecked write-cursor found in s144

s144 read both slot-buffer consumer functions end-to-end (pure source
read, no rebuild) and found a concrete, source-confirmed bug — read
PORTING-STATE's Session 144 entry before doing anything else; this file
only has the actionable summary.

## What s144 did and found

Delegated the two-function read to a subagent (kept ~650 lines of
generated C out of the main context window), then spot-checked the most
load-bearing claim directly (`funcs_24.c:2610-2680`) before trusting it.

**+0x34 refuted for both consumers.** Neither `musyxMixActiveVoices`
(`funcs_24.c:2477-2811`) nor `musyxBuildVoiceCommandList`
(`funcs_24.c:2812-3121`) ever computes a `+0x34` byte offset into a
slot-derived, 136-byte-stride item. This closes s143's headline
question: these two consumers are not the direct writer of the
corruption via their own indexing math.

**Found instead: a real unbounded-write bug.** `musyxMixActiveVoices`
maintains a persistent **global** write-cursor at `0x80149710`
(slot 0) / `0x80149712` (slot 1) — one halfword per slot, read
pre-increment as the item index into the toggle-selected buffer, scaled
by `idx*136`, then incremented and stored straight back
(`funcs_24.c:2648-2664, :2673-2674` and 4 parallel sites). **No
comparison against any voiceCount/capacity value exists anywhere in the
function.** The only thing that indirectly limits how many times it
increments is a *different* global (`0x80149700`) bounding an unrelated
source-side scan loop — not this buffer's own `(voiceCount+1)*136`
allocation size.

`musyxBuildVoiceCommandList` then consumes that exact same unchecked
cursor value as its own loop bound (handed to it as argument `a1` by its
caller `musyxSynthFrame`, `funcs_24.c:3299-3300`), again with no
re-validation.

Confirmed no mutex/lock exists in either function, and
`musyxMixActiveVoices` independently re-reads the toggle byte (which
`musyxSynthFrame` flips asynchronously every VI-retrace tick) 5 separate
times per call rather than caching it once — a real timing hazard,
not yet proven to matter.

**Reframing:** Thread B's leading hypothesis is no longer "which
`rs_malloc` allocation is heap-adjacent to the voice array" — it's now
"does `musyxMixActiveVoices`'s write-cursor overrun its slot's actual
allocated item count, and if so does the resulting out-of-bounds write
land somewhere that explains the arrayBase `+0x34` corruption" (the
corruption's victim is `arrayBase=0x801714D0`+, a *different* buffer
than the slot pair — the connection, if real, is spatial/heap-adjacency,
the same open question s138-143 had, now with a concrete mechanism
instead of an unidentified writer).

## Do next: instrument the write-cursor vs. its slot's actual capacity

This is a rebuild + instrument work unit (bigger than s142-144's pure
source reads) — budget it as one full iteration.

1. Find where `allocateSongChannelArray` (`funcs_23.c:11033`,
   `:11011`) computes `N`/`voiceCount` for the two slot allocations, to
   get the real per-slot item capacity (`(voiceCount+1)` items, 136B
   each) at allocation time. This is a quick source re-read, not a new
   grep — s141/s142 already located the call sites.
2. Land an instrument at `musyxMixActiveVoices`'s cursor read/increment
   site (`funcs_24.c:~2648-2664`) that logs, on every increment: the
   pre-increment cursor value, the toggle-selected slot (0 or 1), and
   (if reachable without a second global lookup) the capacity from step
   1. Gate it `ROGUESQ_LOG_VOICE_CURSOR=1`.
3. Positive control: the log must fire on every voice-active hit (same
   shape as s143's `[rs-malloc-site]` control, 12/12).
4. Discriminating question: does the logged cursor value ever reach or
   exceed the slot's actual allocated capacity in the same run that
   produces a `do_rom_read`/arrayBase corruption hit? If yes, this is a
   strong second source for a genuine out-of-bounds write mechanism (not
   yet a proof it's THE corruption's writer — that needs a heap-layout
   argument, same as the original Thread B adjacency question). If the
   cursor never exceeds capacity in a run that still shows the
   corruption, that refutes this specific mechanism and Thread B falls
   back to s143's parked "toggle desync" timing hypothesis.
5. Do NOT also build the toggle-desync instrument in the same session —
   pick this one, per rule 8's spirit of not stacking speculative work.

## Do not

- Do not re-read `musyxMixActiveVoices`/`musyxBuildVoiceCommandList` —
  s144 read both end-to-end and confirmed no `+0x34` access exists in
  either. That question is closed.
- Do not re-grep for candidate B's consumer — s143 already found and
  named it.
- Do not re-characterize `allocateSongChannelArray`'s own write pattern
  — s142 exhausted that.
- Do not re-guess `setupSongRenderBuffers` or `buildSongDecodeBufferRing`
  as producers of 8568/32768 — directly refuted, s141.
- Do not re-search the audio boot files for candidate A's overlay-load
  producer — separate, still-open lead (s141), not this thread's focus.
- Do not re-audit any of Thread A's 8 hangar-tick-family functions —
  closed, s90-137.

## This session's environment notes (carry forward, still current)

- Delegating a multi-hundred-line function read to a subagent (Explore,
  foreground) worked well again — gave it the full address-decode
  context and the exact questions up front, got back a structured report
  with file:line citations, then spot-checked the single most
  load-bearing claim directly instead of re-reading everything. Prefer
  this shape for any "read N functions and answer specific questions"
  task; always spot-check at least the headline claim before writing it
  into docs.
- N64Recomp's codegen convention for a fixed-global access: writes are
  `MEM_W(<offset>, ctx-><base>) = ctx-><src>;`; reads flip the argument
  order to `ctx-><dst> = MEM_W(ctx-><base>, <offset>);`.
- Function boundaries in generated `.c` files are NOT reliably where a
  NEXT.md estimate guesses — always confirm against the actual
  `RECOMP_FUNC`-marker boundaries (s144 found
  `musyxBuildVoiceCommandList` ends at `:3121`, ~180 lines short of the
  `:3300` estimate).
- `[rs-malloc-site]`-to-`[rs-malloc]` correlation-by-log-order technique
  (12/12 positive control, s141) generalizes to any call-site-attribution
  problem where `caller_ra` is unusable.
- `rs_malloc`'s real argument order is `(size, flags)` — confirmed s139.
- `rs_free`'s real argument is `(ptr)` — confirmed s140.
- `caller_ra` (`ctx->r31` at function entry) reads `0x00000000`
  universally — stop treating it as a signal (s92, s139, s140, s141).
- When reading recompiled `.c` for a fixed guest global address, remember
  different call sites can reach the same address via different
  `lui`-page/offset splits — for this pair (`0x80149708`/`0x8014970C`
  slots, `0x80149702` toggle, `0x80149700`/`0x80149710`/`0x80149712`
  counters/cursors) the full decode is now resolved (s143/s144).
- `rm` on paths outside `scratch/` requires approval and does NOT accept
  glob patterns — use a `python3 -c` one-liner with `pathlib.Path.glob()`.
- Do NOT re-run `fixup_game_funcs.py` a second time in the same session
  without a full regen first (non-idempotent, s102) — delete
  `RecompiledFuncs/funcs_*.c`, re-run `make_elf.py` (cwd
  `~/Documents/Tools/rogue_squadron64`), then
  `zsh tools/agent/regen_n64recomp.sh` (cwd this repo, NOT `N64Recomp`),
  THEN `fixup_game_funcs.py` once (cwd `N64Recomp`) — verify by grepping
  the regenerated `.c` directly.
- `cmake --build` needs cwd `build/` and
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` for Metal
  shader rebuilds.
- Write a new wrapper script file per soak tag (`scratch/agent/run_
  <tag>.sh`) rather than parametrizing a single reusable script via env
  indirection.
- A `run_mission_keys.sh` soak with `run_in_background: true` works, but
  block on it synchronously before closing out the iteration (the Stop
  hook can't see backgrounded work in flight) — e.g. `until ! pgrep -f
  "./RogueSquadron64Recomp" >/dev/null 2>&1; do sleep 5; done`.
- Checking submodule (`lib/...`) git status needs `env GIT_DIR=lib/X/.git
  GIT_WORK_TREE=lib/X git status --short`, or a plain `cd <absolute
  path>` as its own command followed by a separate `git status` call.
- Output redirection (`>`) from Bash is sandboxed to the session's
  allowed working directories — target `scratch/agent/`, not `/tmp`.
- Prefer a single `python3 - <<'EOF' ... EOF` heredoc for multi-step log
  analysis instead of chaining many small grep/echo commands.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is well over the ~35 KB target (2400+ lines,
growing). Migrate durable mechanism/architecture material to
PROJECT-OVERVIEW.md and prune superseded detail, paired with a real
experiment — not on its own.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-144
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.
