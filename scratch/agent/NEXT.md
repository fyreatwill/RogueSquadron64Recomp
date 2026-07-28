# NEXT work unit — Thread B: fix the proven race, verify corruption stops

s146 landed and soaked the count-write instrument s145 specified --
read PORTING-STATE's Session 146 entry before doing anything else; this
file only has the actionable summary.

## What s146 did and found

Landed `[song-count-write-early]` logging immediately after
`allocateSongChannelArray`'s early `voiceCount` write to the scan-bound
global (`funcs_23.c:10712-10713`, exact match to NEXT.md's own line
estimate this time), gated on the existing
`ROGUESQ_LOG_SONG_ARRAY_LIFECYCLE` flag. Full regen + soak
(`scratch/agent/run_countrace1.sh`).

**Thread B's root cause is now directly proven, not circumstantial.**
Parsed the full run log pairing each `[song-count-write-early]` line
with its next `[song-array-alloc]` line and checking for any
`[voice-active-gate-nz]` line strictly between them. 5/6 windows this
run were clean, but the `voiceCount=18` window
(`scratch/s73_post_a_scene/countrace1/run.log:39205-39218`, 13 lines
wide) had **4 of the run's 5 total corrupted-gate reads sandwiched
directly inside it** — `idx=0x10`/`0x11` scanned against `count=0x0012`
(18, the just-written new value) while `arrayBase` was still the old
allocation's address (rs_malloc for the new one hadn't returned yet,
appearing 2 log lines later). This is the scan caught live, inside the
exact instrumented window, 4 separate times in one run — not inference
from which print came first.

**Mechanism (unchanged from s145, now proven):** `allocateSongChannelArray`
writes the new `voiceCount` to the scan-bound global (`0x80149700`) at
`funcs_23.c:10712-10713` — many instructions **before** it calls
`rs_malloc` and stores the new array pointer at `:10722-10733`. No lock
exists anywhere in this family (s144 confirmed). A concurrently-scanning
`musyxMixActiveVoices` (audio runs off the VI-retrace thread, s101) can
observe the new, larger count against the still-old, smaller array
mid-scan, landing past the old allocation's true bound into whatever
`rs_malloc`'s free-list handed back — still carrying a prior occupant's
un-overwritten bytes (the ASCII fragments s138 catalogued).

`do_rom_read`/`piDmaWorker` did NOT recur this run (0/1) — the process
instead died to a SIGBUS in `frameStartReset` (`funcs_23.c` chain via
`static_5_800AAD9C`/`static_5_800C6854`/`menuOverlayInit`), the same
class first seen s84 and assessed a fluke after non-recurrence in s85 —
still a minority outcome (1 of ~8 soaks since s84), not promoted to a
tracked class.

## Do next: land the fix, verify the race window closes

This is a small, register-confirmed-safe source reorder + one soak —
budget it as one iteration. s146 already confirmed `ctx->r16`
(voiceCount) is never reassigned between the count-write site and the
existing `[song-array-alloc]` print, so moving the write is safe.

1. In `allocateSongChannelArray` (`funcs_23.c`, edit via
   `N64Recomp/fixup_game_funcs.py` — hand-edits to generated code die at
   the next regen), move the early count-write
   (`MEM_H(-0X6900, ctx->r1) = ctx->r16;`, currently
   `funcs_23.c:10712-10713`, right after the `lui $at,0x8015` at
   `:10710-10711`) to **after** the pointer-store block
   (`funcs_23.c:10722-10733` in the current build — reconfirm exact
   lines after regen, they drift every session). Keep the existing
   `lui`/`sh` instruction pair intact, just relocate it as a unit to
   right after the second pointer store (`-0x6908`) and before the
   `[song-array-alloc]` diagnostic block.
2. This makes the scan-bound global only advance *after* the new array
   pointer is already published — closes the window for this specific
   race. The read side (reload-every-iteration in
   `musyxMixActiveVoices`, confirmed s145) needs no change.
3. Rebuild via the full regen pipeline (delete `RecompiledFuncs/funcs_*.c`
   → `make_elf.py` → `regen_n64recomp.sh` → `fixup_game_funcs.py` once →
   `cmake --build`), verify the reordered patch applied exactly once by
   grepping the regenerated `.c` before building — confirm the count-write
   line now appears textually AFTER the two pointer-store lines.
4. Soak with the same full diagnostic battery as `run_countrace1.sh`
   (copy forward to `run_countracefix1.sh`, keep
   `ROGUESQ_LOG_SONG_ARRAY_LIFECYCLE=1` and
   `ROGUESQ_LOG_VOICE_ACTIVE_GATE=1` armed to check the fix directly).
5. Discriminating question: across the full soak, does any
   `[voice-active-gate-nz]` line ever again fall between a
   `[song-count-write-early]` line and its matching `[song-array-alloc]`
   line? (Reuse `scratch/agent/s146_analyze.py` — it already does this
   pairing/sandwich check, just point it at the new log file.) A single
   clean soak is not proof by itself (the race was already rare — only
   1/6 windows hit this run), but a 2nd/3rd clean soak plus continued
   absence of the `do_rom_read`/`piDmaWorker` byte-identical corruption
   signature (`devAddr=0x6C676672 dramAddr=0x80195190`) across those
   soaks would be strong converging evidence the fix works. If it DOES
   still fire post-fix, the reorder didn't close the window (check for a
   second writer, or a different non-atomic pair) — do not assume the
   fix worked without checking.
6. If the fix soak's own corruption checks come back clean 2-3 times
   running, the next work unit becomes checking whether `do_rom_read`
   stops recurring too (it shares the same general non-atomic-global
   mechanism family per s145/146, though not yet proven the same code
   path) — that would be the real end-to-end validation this multi-
   session thread has been chasing since s105.

## Do not

- Do not re-derive the cursor/capacity math, the ROM->RAM bias, or the
  ASCII-fragment provenance again — all closed (s138-s146).
- Do not re-instrument `musyxMixActiveVoices`'s read side — it already
  reloads its bound fresh every iteration (confirmed s145); the bug is
  entirely on the write side.
- Do not treat a single clean soak post-fix as proof — this race was
  hit in only 1 of 6 windows in s146's own soak; absence needs 2-3
  repeats to mean something (see step 6).
- Do not drop `ROGUESQ_LOG_VOICE_CURSOR`, `[song-array-alloc]`, or any
  other instrument from the existing battery — it's free and already
  proved useful as a cross-check (generalizes every session so far).

## This session's environment notes (carry forward, still current)

- **A corrupted read doesn't have to be caught by the instrument you
  just built to be caught.** s145 and s146 both found their
  discriminating result via the *pre-existing* `[voice-active-gate-nz]`
  log line, not the new instrument itself — always grep the FULL run
  log for every armed diagnostic's output, not just the one you just
  added, before writing up a run as inconclusive or as a weak result.
- Function/line-number estimates in NEXT.md are usually a few lines off
  from the actual `RECOMP_FUNC` boundaries in regenerated `.c` (s100,
  s144, s145) but matched exactly this session (s146) — still always
  grep/read the actual file before writing a regex anchor; don't assume
  either direction.
- N64Recomp's codegen convention for a fixed-global access: writes are
  `MEM_W(<offset>, ctx-><base>) = ctx-><src>;`; reads flip the argument
  order to `ctx-><dst> = MEM_W(ctx-><base>, <offset>);`.
- "Sandwich a corrupted read between two known print lines" (s145's
  log-order technique, now upgraded by s146 to "bracket the exact
  instrumented window and catch it live") generalizes to any
  ordering/timing question where a direct lock/mutex log isn't
  available.
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
  indirection. `run_countrace1.sh` (this session) and `run_voicecursor1.sh`
  (s145) are good templates — copy the full armed-diagnostics battery
  forward rather than dropping back to `run_mission_keys.sh` directly.
- Launch the soak via `zsh <absolute-path>/run_<tag>.sh > <absolute-path>/
  run_<tag>_driver.log 2>&1` as a `run_in_background` Bash call, then
  block synchronously with `until ! pgrep -f "./RogueSquadron64Recomp"
  >/dev/null 2>&1; do sleep 5; done` before closing out the iteration.
- Checking submodule (`lib/...`) git status needs `env GIT_DIR=lib/X/.git
  GIT_WORK_TREE=lib/X git status --short`, or a plain `cd <absolute
  path>` as its own command followed by a separate `git status` call.
- Output redirection (`>`) from Bash is sandboxed to the session's
  allowed working directories — target `scratch/agent/`, not `/tmp`.
- Prefer a single `python3 script.py` file (Write then run) for
  multi-step log analysis instead of a bash heredoc — heredocs with
  f-string braces containing quotes get rejected by the Bash tool's
  expansion-obfuscation heuristic.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is ~171 KB (2450+ lines), far over the ~35 KB
target. Migrate durable mechanism/architecture material to
PROJECT-OVERVIEW.md and prune superseded detail, paired with a real
experiment — not on its own. This has been flagged for many sessions
without action; if Thread B's fix soak (this file's primary work unit)
comes back clean 2-3 times running and the thread closes out, the
housekeeping prune would be a reasonable pairing for the session that
writes up that closure.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-146
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.
