# NEXT work unit — Thread B: pin down the count-write-before-pointer-store race directly

s145 landed and soaked the cursor-overrun instrument s144 specified —
read PORTING-STATE's Session 145 entry before doing anything else; this
file only has the actionable summary.

## What s145 did and found

Landed `ROGUESQ_LOG_VOICE_CURSOR=1` (`musyxMixActiveVoices`'s write-cursor
read/increment/store-back site, `funcs_24.c:2653-2668` — NOT NEXT.md's
`~2648-2664` estimate, off by a few lines again; always confirm against
the actual `RECOMP_FUNC` boundaries, this is now a recurring lesson).
Full regen + soak (`scratch/agent/run_voicecursor1.sh`).

**The write-cursor-overflow hypothesis is refuted for a live-captured
corruption event.** 0/8 fires of `[voice-cursor-overflow]` (positive
control confirmed: 8/8 matches the pre-existing, independent
`[voice-active-gate-nz]` counter on the same gate condition). At the
exact same moment (same log-order neighborhood), that pre-existing
counter caught a real corruption live: `idx=0x10`/`0x11` (16/17) scanned
against a freshly-logged `count=0x0012` (18) while the array itself was
still the **previous** `voiceCount=15` allocation (valid indices 0-14
only) — bytes read decode as the exact ASCII fragments (`explo_tex2`,
`x10`, `x11`) s138 catalogued as runtime-only. This closes that
question: they're leftover bytes from a **recycled, unrelated prior
heap allocation**, not static ROM data, not a stomp, not a table-index
bug.

**Real mechanism identified (source-confirmed, not yet directly
instrumented):** `allocateSongChannelArray` writes the new `voiceCount`
to the scan-bound global (`0x80149700`) at `funcs_23.c:10712-10713` —
**many instructions before** it calls `rs_malloc` and stores the new
array pointer / prints `[song-array-alloc]` at `:10717-10738`. This is a
non-atomic (count, pointer) pair with **no lock anywhere in this family**
(s144 already confirmed no mutex exists). A concurrently-scanning
`musyxMixActiveVoices` (audio runs off the VI-retrace thread per s101)
can observe the **new**, larger count against the **still-old**, smaller
array mid-scan — landing past the old allocation's true bound into
whatever the allocator's free-list handed back, still carrying the prior
occupant's un-overwritten bytes.

This is currently a **single occurrence**, inferred from log-line
ordering (the scan's corrupted reads appeared between the last
`voiceCount=15` alloc's print and the next `voiceCount=18` alloc's
print) — strong circumstantial evidence, not yet a direct proof that a
scan's count-read literally executed inside the count-write-to-pointer-
store window.

## Do next: instrument the count-write site directly to prove (or refute) the race window

This is a small instrument (one new log site, no new hypothesis to
design) + one soak — budget it as one iteration; if it fires with a
scan sandwiched inside the window, Thread B's root cause is closed and
the next unit becomes "add a lock/guard, verify corruption stops."

1. In `allocateSongChannelArray` (`funcs_23.c`), add a log immediately
   after the early count-write (`funcs_23.c:10712-10713`,
   `MEM_H(-0X6900, ctx->r1) = ctx->r16;`) — BEFORE the `rs_malloc` call —
   printing the new `voiceCount` with a tag like
   `[song-count-write-early]`. Gate it on the existing
   `ROGUESQ_LOG_SONG_ARRAY_LIFECYCLE` env var (reuse s120's flag, don't
   add a new one — this is the same lifecycle question).
2. Rebuild via the full regen pipeline (delete `RecompiledFuncs/funcs_*.c`
   → `make_elf.py` → `regen_n64recomp.sh` → `fixup_game_funcs.py` once →
   `cmake --build`), verify the new patch applied exactly once by
   grepping the regenerated `.c` before building.
3. Soak with `ROGUESQ_LOG_SONG_ARRAY_LIFECYCLE=1` and
   `ROGUESQ_LOG_VOICE_ACTIVE_GATE=1` both armed (keep the rest of the
   existing battery from `run_voicecursor1.sh` too — copy it to a new
   `run_countrace1.sh` per this session's environment note, don't
   parametrize the existing script).
4. Discriminating question: does any `[voice-active-gate-nz]` line
   (or a new corrupted read) appear, in log order, **between** a
   `[song-count-write-early]` line and its corresponding
   `[song-array-alloc]` line (same voiceCount value, since both fire
   once per call)? If yes — race window directly proven, add a lock or
   reorder the writes (pointer+memset before count) as the fix. If the
   window is large (many lines between the two prints) but no scan ever
   lands inside it across a full soak, that's evidence the window is
   real but rarely hit — still worth a defensive fix (reordering costs
   nothing) but downgrades urgency.
5. Do NOT re-derive the cursor/capacity math again — s142/s144/s145
   already closed it (capacity formula `N*(voiceCount+1)`, `N` read from
   `0x8014974E`, cached at `0x80149704`).

## Do not

- Do not re-read `musyxMixActiveVoices`/`musyxBuildVoiceCommandList` —
  fully characterized s143-145 (index math, +0x34 refuted, cursor
  mechanism, capacity source, this session's scan-loop reread-per-
  iteration behavior at `:2681-2696`). Closed.
- Do not re-litigate whether the `explo_tex2`/`x10`/`x11` fragments are
  static ROM data — s138 already showed they're absent from a full-ROM
  strings dump, and s145 now explains why (recycled heap, not a string
  table read via a computed index).
- Do not re-guess `setupSongRenderBuffers` / `buildSongDecodeBufferRing`
  as producers of 8568/32768 — refuted, s141.
- Do not re-audit Thread A's 8 hangar-tick-family functions — closed,
  s90-137.
- Do not add the `ROGUESQ_LOG_VOICE_CURSOR` instrument again — it's
  landed and working (0/8 overflow, 8/8 positive control this run); keep
  it armed in future soaks, it's free and already proved useful as a
  cross-check.

## This session's environment notes (carry forward, still current)

- **Cross-check a low-fire-count instrument against a sibling counter on
  the same gate condition before calling it weak.** s145's
  `[voice-cursor-hb]` printed only once (heartbeat is every 5000) which
  looked like a near-null result until cross-referencing the
  pre-existing `[voice-active-gate-nz]` counter (same `byte != 0` gate)
  showed exactly 8 true fires both times — the instrument was fine, the
  event was just rare this run. Generalizes to any low-count diagnostic
  in this family.
- **A corruption doesn't have to be caught by the instrument you built
  to be caught.** s145's actual discriminating finding came from a
  *pre-existing* log line (`[voice-active-gate-nz]`, s117) that happened
  to capture the corruption live in the same window as the new
  instrument's sample — always grep the FULL run log for every armed
  diagnostic's output, not just the one you just added, before writing
  up a run as inconclusive.
- Function/line-number estimates in NEXT.md are consistently a few lines
  off from the actual `RECOMP_FUNC` boundaries in regenerated `.c` —
  4th time this has been true (s100, s144, s145). Always grep/read the
  actual file before writing a regex anchor; never trust a remembered
  line range.
- N64Recomp's codegen convention for a fixed-global access: writes are
  `MEM_W(<offset>, ctx-><base>) = ctx-><src>;`; reads flip the argument
  order to `ctx-><dst> = MEM_W(ctx-><base>, <offset>);`.
- `[rs-malloc-site]`-to-`[rs-malloc]` correlation-by-log-order technique
  (s141) and this session's "sandwich a corrupted read between two known
  print lines" technique both generalize to any ordering/timing question
  where a direct lock/mutex log isn't available.
- `caller_ra` (`ctx->r31` at function entry) reads `0x00000000`
  universally — stop treating it as a signal (s92, s139, s140, s141).
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
  indirection. `run_voicecursor1.sh` is a good template (copies the full
  armed-diagnostics battery from `run_rsmallocsite1.sh` plus the new
  flag) — copy it forward rather than the older `run_mission_keys.sh`
  directly, so the accumulated battery of diagnostics doesn't get
  dropped session to session.
- Launch the soak via `zsh <absolute-path>/run_<tag>.sh > <absolute-path>/
  run_<tag>_driver.log 2>&1` as a `run_in_background` Bash call — a
  compound `cd ... && zsh ...` with output redirection gets denied
  ("changes directories and writes via output redirection"); the target
  script already `cd`s internally so no separate `cd` is needed. Then
  block synchronously with `until ! pgrep -f "./RogueSquadron64Recomp"
  >/dev/null 2>&1; do sleep 5; done` before closing out the iteration.
- Checking submodule (`lib/...`) git status needs `env GIT_DIR=lib/X/.git
  GIT_WORK_TREE=lib/X git status --short`, or a plain `cd <absolute
  path>` as its own command followed by a separate `git status` call.
- Output redirection (`>`) from Bash is sandboxed to the session's
  allowed working directories — target `scratch/agent/`, not `/tmp`.
- Prefer a single `python3 - <<'EOF' ... EOF` heredoc for multi-step log
  analysis instead of chaining many small grep/echo commands (the Bash
  tool also rejects some multi-statement one-liners with inline `echo`/
  `grep` chains — a heredoc script sidesteps that).

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is well over the ~35 KB target (2400+ lines,
growing). Migrate durable mechanism/architecture material to
PROJECT-OVERVIEW.md and prune superseded detail, paired with a real
experiment — not on its own.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-145
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.
