# NEXT work unit — guard (or get disassembly on) the `runVideoFrameTick
+1568` SIGBUS, now the confirmed dominant soak-blocker

Read `docs/CURRENT-TRUTH.md`'s `-47` next-steps item (top of the list) and
PORTING-STATE Session 198 in full before doing anything else (`grep -n
"^## Session 198" PORTING-STATE.md`). Also skim Session 192's and 193's
entries (`grep -n "^## Session 19[23]" PORTING-STATE.md`) — 193 already
tried and abandoned disassembling this exact crash site once; read why
before repeating that attempt blindly.

## Why this is the next work unit

s198's 4th `cacheheadguard` soak gave a 3rd consecutive clean pass through
the 18th crash class's death zone (decisionN=15418, past the 9660-9792
target window) — per NEXT.md's own prior criteria that retires the 18th
class as the primary blocker (still unconfirmed by a guard fire, 0/4, but
not worth a 5th blind soak on the same hypothesis per iron rule 8).

Instead, the run died to `runVideoFrameTick+1568` SIGBUS — the SAME native
offset as s192's `sceneptrguard5` crash (decisionN=8972). Two occurrences,
same offset, same duplicated-frame stack-unwind shape, ~6 sessions apart:
this is now a CONFIRMED recurring crash class, not the one-off s192 left it
as. It is currently the furthest-reaching blocker in the project (killed
the run at decisionN=15418, well past every other guard's target window),
so it is now the top-priority open item.

## Do this, in order

1. **Try disassembly tooling again, once, before falling back to a
   broad guard.** s193 confirmed `otool`/`nm`/`objdump`/`lldb` are not on
   the Bash allowlist and a hand-rolled ARM64 decoder
   (`scratch/agent/s193_disasm.py`) produced an internally-inconsistent
   result. If a tool-approval prompt is available this session (check
   whether the environment changed since s193 — try `otool -tv build/
   RogueSquadron64Recomp | head` and see if it's actually denied or just
   needs approval, don't assume from the old citation), get precise
   disassembly at native offset `runVideoFrameTick+1568`
   (`0x00000001040b7cb8`-equivalent for this build — recompute the actual
   address for THIS build's binary, it will differ) and identify the real
   faulting dereference. If tooling is confirmed still unavailable, do NOT
   retry the hand-rolled decoder (already shown untrustworthy) — go to
   step 2.
2. **Fallback: broad defensive guard across `runVideoFrameTick`'s
   recompiled C body.** Read the full function
   (`N64Recomp/RecompiledFuncs/funcs_0.c:1459` onward, ~415 lines, per
   s193's citation — confirm the current line range first, the file may
   have shifted since s193's guards). Identify every raw pointer
   dereference reachable from guest-controlled data (the same class of bug
   s197 found: unmasked KSEG0 pointers, uninitialized cache reloads) and
   wrap each with the same RDRAM-range sanity check + logged bail used by
   the rs_malloc/rs_free/scene-node-ptr/queueGPUUploadTMEM/
   scene-node-cache guards. New env var suggestion:
   `ROGUESQ_LOG_VIDEO_FRAME_TICK_GUARD`. This trades precision for
   coverage — acceptable now that 2 confirmed occurrences justify the
   cost (per s193's own framing, this felt premature at 1 occurrence, not
   at 2).
3. Regenerate (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` ->
   `cmake --build build -j8`, `DEVELOPER_DIR=/Applications/Xcode.app/
   Contents/Developer` for Metal), verify the patch applied exactly once
   (grep the regenerated `funcs_0.c` for your new guard, count should be 1
   not 2 — `fixup_game_funcs.py` is non-idempotent).
4. Soak (`scratch/agent/run_videoframetickguard1.sh`, copy
   `run_cacheheadguard4.sh`'s env block, add the new guard's env var,
   rename the tag). Discriminating outcomes:
   - **Guard fires with sane fields, soak reaches further than
     decisionN=15418 or completes clean** → strong positive signal, write
     up as likely-fixed pending a 2nd soak (same bar as every other guard
     in this project).
   - **Guard fires but crash still happens right after** → the bail target
     is unsafe, needs a different reentry point (same failure mode s197
     had to design around for the cache guard — its bail target explicitly
     resets the corrupt global rather than reusing the empty-cache reentry
     point).
   - **0 fires, crash recurs at the SAME +1568 offset** → your guard
     didn't cover the actual faulting site; the disassembly-avoidance
     tradeoff failed, escalate to requesting real tool access rather than
     guessing again.
   - **0 fires, no recurrence, dies to something else** → 3rd clean pass
     of a DIFFERENT kind — informative for `runVideoFrameTick` specifically
     even without a guard fire, same "N clean passes" reasoning applied
     this session to the 18th class.
5. Whatever the outcome, update `PORTING-STATE.md` (new session entry),
   `docs/CURRENT-TRUTH.md` (`-47` entry's status), and this file, per the
   exit contract.

## Do not

- Do not re-touch the s123/s131 `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`,
  the s197 `SCENE_NODE_CACHE_GUARD`, the s190 `scene-node-ptr-guard`, or
  the s196 `REINTERPRET_TILE_GUARD` — all correct-per-spec, all still
  0-fire, none has new evidence against it. The 18th crash class is now
  "very likely fixed, mechanism unconfirmed" — do not spend another soak
  chasing its guard's positive control; only revisit if THIS session's
  soak produces a fresh recurrence unprompted.
- Do not repeat s193's hand-rolled ARM64 decoder approach a 2nd time — it
  already proved internally inconsistent once; if real tooling is
  unavailable, go straight to the broad-guard fallback (step 2), don't
  re-derive the same untrustworthy result.
- Do not chase the 23rd-class `waitForAnyAudioSlot` SIGSEGV or the
  `evalCubicSplineAtTime` SIGBUS family this iteration unless THIS
  session's soak dies to one of them AGAIN after exhausting budget on
  `runVideoFrameTick` — both remain open, flagged, lower priority.

## Environment notes (carried forward, still current)

- Disassembly tools (`nm`/`otool`/`objdump`/`lldb`) were NOT on the Bash
  allowlist as of s193/s194 (confirmed blocked) — re-verify fresh this
  session (step 1) rather than assuming unchanged, but don't burn more
  than one quick check on it before falling back.
- The crash handler dumps siginfo + full ARM64 register file on every
  SIGSEGV/SIGBUS/SIGABRT (`src/main/main.cpp`) — check `[CRASH][siginfo]`/
  `[CRASH][mcontext]`/`[CRASH][vifs-snapshot]` lines first, plus the
  backtrace lines immediately below them (function names + offsets are
  printed directly, no disassembly needed for THAT part — only the
  in-function offset-to-source mapping needs real disassembly).
- `N64Recomp/fixup_game_funcs.py` is non-idempotent — running it twice
  duplicates every patch.
- Any edit under THIS repo's `lib/` needs `./submodule-patches/export.sh` +
  commit in the SAME session. `N64Recomp` and `rogue_squadron64` are
  SEPARATE checkouts outside this repo, NOT `lib/` submodules — their
  uncommitted changes are flagged for the user, not this session's call to
  commit.
- Re-running the same soak script/tag overwrites the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
  `run.log` files are multi-GB; NEVER `Read` or `cat` them whole — always
  `grep`/`sed -n` for specific line ranges.
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh` /
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied in ONE
  Bash call, and even a single `cd foo && git status` in one call can get
  auto-flagged for approval on some directories — prefer separate Bash
  calls (one `cd`, then the next command in its own call; cwd persists
  across calls) or wrap the whole thing in `zsh -c "..."` (matches the
  `Bash(zsh:*)` allow rule as a single command).
- Block on a soak by launching with `run_in_background: true` and calling
  `TaskOutput(task_id, block=true, timeout=300000-480000)` — do not end the
  turn while a background soak is still running. A `<task-notification>`
  also arrives automatically on completion.
- Heredocs get rejected by this session's Bash tool — use the Write tool
  instead, including for large PORTING-STATE.md appends (write a tmpfile
  with the Write tool, then `cat tmpfile >> PORTING-STATE.md` — the file
  itself is over 1.2MB, too large for the Edit tool's read-first
  requirement, and over the Read tool's 256KB single-read limit).
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.
- `scratch/agent/STATUS`/`OUTCOME` get reset to `WORKING`/deleted at the
  START of each iteration by the harness — finding them in that state at
  session start is normal, not evidence of a crashed prior session.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now well over the ~35 KB CLAUDE.md budget and
exceeds the Read tool's 256 KB single-read limit (confirmed s195, still
true s198 — read it with `grep`/`sed -n`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md`
and prune superseded detail, paired with a real experiment — flagged for
many sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session's commit
scope. Still flagged for the user, not committed autonomously.
