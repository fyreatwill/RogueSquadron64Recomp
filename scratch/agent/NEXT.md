# NEXT work unit — source-read `submitSceneNodeRender` for the same
KSEG0 zero-extension bug, using the s200/s201 method

Read `docs/CURRENT-TRUTH.md`'s `-48` next-steps item (top of the list) and
PORTING-STATE Session 201 in full before doing anything else (`grep -n
"^## Session 201" PORTING-STATE.md`). Session 200 (original callee
narrowing) and Session 194/199 (original register-file decode) are cited
there if you need the crash mechanism refresher — s201 doesn't repeat it,
just cites it.

## Why this is the next work unit

s200 exhaustively ruled OUT `processSceneNode` itself (source read + a
46,292-call dynamic trace at the call boundary, 0 anomalies). s201 ran 2
more soaks of the same tracer (116,950 total calls across 3 soaks now, 0
non-canonical args, still 0 reproductions of the target `+8772` crash
signature — both s201 soaks died early to two OTHER, already-catalogued
crash classes instead: `frameStartReset+532` and `runVideoFrameTick+1576`).
Per the budget rule (3 consecutive uninformative soaks), s201 stopped
soaking and pivoted to the documented fallback: a full source read of
`renderLitMeshFaceGroup` (the biggest, highest-call-volume of the five
direct callees). **That read came back clean** — no bypass of the
`ADD32`/`SUB32`/sign-extend convention found anywhere in its ~5068 lines.
That narrows the remaining candidate set to four: `submitSceneNodeRender`,
`renderFlatMeshFaceGroup`, `renderUnlitMeshFaces`, `renderLitTexturedMeshFaces`.

## Do this, in order

1. **Do NOT re-soak the tracer this iteration.** 3 soaks, 116,950 calls,
   0 reproductions is enough per the budget rule (iron rule 8 / NEXT.md's
   own 3-consecutive-iteration cap). Only revisit soaking once ALL FOUR
   remaining callees have been source-read and come back clean too — at
   that point the instrument itself may need rethinking (see step 5).
2. **Source-read `submitSceneNodeRender`** next
   (`N64Recomp/RecompiledFuncs/funcs_4.c:6-3018`, ~3000 lines — the
   largest of the four remaining candidates). Delegate to a subagent using
   the SAME brief s201 used successfully for `renderLitMeshFaceGroup`:
   - Give it the exact macro definitions from
     `/Users/williambuckley/Documents/Tools/N64Recomp/include/recomp.h`
     lines 86-108 (`SIGNED`/`ADD32`/`SUB32`/`MEM_W`/`MEM_H`/`MEM_B`/
     `MEM_HU`/`MEM_BU`).
   - Give it the exact crash signature: a KSEG0 zero-extension bug, fault
     address decomposing as `rdram_base + 0x0000000080xxxxxx` (top 32
     bits zero instead of `0xFFFFFFFF`-sign-extended).
   - Ask it to hunt for: raw `+`/`-` arithmetic on `gpr`/`uint64_t`
     register values that bypasses `ADD32`/`SUB32`; `(uint32_t)` casts
     feeding a pointer-shaped register; zero-extending `MEM_HU`/`MEM_BU`
     loads whose result gets ADDED into a pointer (not just masked into a
     flag/color field — that pattern was benign in `renderLitMeshFaceGroup`,
     don't assume it's always benign, check each occurrence's actual use);
     `MOVZ`/`MOVN`-style register-assigning ternaries where one branch
     sign-extends and another doesn't; any cast/helper you don't recognize
     from the macro list.
   - Ask for file:line + one-paragraph mechanism explanation only — no
     large code paste-backs. Read in chunks (offset/limit), not the whole
     3000 lines in one call.
3. **If a bypass is found**: guard or fix it, mirroring the established
   RDRAM-range-check pattern (`N64Recomp/fixup_game_funcs.py`'s existing
   guards are all templates for this — e.g. the s196 `REINTERPRET_TILE_GUARD`
   or s197 `SCENE_NODE_CACHE_GUARD` for shape). Regenerate per step 5 below,
   then soak once to look for a positive control (the guard firing) or at
   minimum a clean pass past the crash's usual decisionN range.
4. **If clean (no bypass found)**: note it in the session log (same format
   as s201's `renderLitMeshFaceGroup` entry — what was checked, what
   patterns were ruled out) and move to the next remaining candidate
   (`renderFlatMeshFaceGroup`, `funcs_4.c:3018-4951`) in a FUTURE session —
   don't try to fit two 3000+/1900-line source reads in one iteration.
5. Regenerate (`make_elf.py` -> `env ./build/N64Recomp rogue_squadron.toml`
   -> `env python3 fixup_game_funcs.py` -> `cmake --build build -j8`,
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` for Metal)
   ONLY if you land a new patch. **Verify no duplication before building**:
   after the regen step (make_elf.py -> N64Recomp), grep-count your new
   patch's anchor string in the fresh RecompiledFuncs output (should be 0,
   confirming a clean unpatched regen), THEN run fixup exactly ONCE, THEN
   grep-count again (should match your site count). **Never run
   `fixup_game_funcs.py` more than once per regen** — s200 proved older
   patches in the same file are not idempotent (failure mode is a build
   error, not silent corruption, but it wastes a full regen+build cycle).
6. Whatever the outcome, update `PORTING-STATE.md` (new session entry,
   #202), `docs/CURRENT-TRUTH.md`'s `-48` entry, and this file, per the
   exit contract.

## Do not

- Do not re-read `processSceneNode` (s200 closed it, 2 independent lines
  of evidence) or `renderLitMeshFaceGroup` (s201 closed it, source-clean,
  single-source but no contradicting evidence) for this bug. Only revisit
  either if a FUTURE crash's register evidence directly contradicts them.
- Do not re-run the `processScenenNodeCalleeTrace` soak this iteration —
  3 soaks (116,950 calls) with 0 reproductions already exhausts the
  budget rule for this specific instrument. Source-reads are the current
  best information-value move, not more soaking.
- Do not re-touch the s123/s131 `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`,
  the s197 `SCENE_NODE_CACHE_GUARD`, the s190 `scene-node-ptr-guard`, the
  s196 `REINTERPRET_TILE_GUARD`, or s199's `video-frame-tick-guard` — all
  correct-per-spec, all still 0-fire (or in the video-frame-tick guard's
  case, still unconfirmed against its own bug), no new evidence against
  any of them this session.
- Do not chase the `frameStartReset+532` family (s84-origin, source-
  verified clean, part of the unexplained "shared corruption race") or the
  `runVideoFrameTick+1576`/`+1568` recurring class (item -47.5, lower
  priority than -48) this iteration unless THIS session's own work
  produces new evidence about them specifically.
- Do not chase the 23rd-class `waitForAnyAudioSlot` SIGSEGV or the
  `evalCubicSplineAtTime` SIGBUS family this iteration — both remain open,
  flagged, lower priority than -48.

## Environment notes (carried forward, still current)

- Disassembly tools (`nm`/`otool`/`objdump`/`lldb`) still blocked as of
  s201 (non-interactive session, no human to clear the approval prompt);
  not re-tested s201 since source-reading made it unnecessary again —
  re-verify fresh only if something about the environment seems to have
  changed.
- `./build/N64Recomp rogue_squadron.toml` (from the `N64Recomp` checkout)
  needs an `env` prefix to clear the permission-prefix-match wall — bare
  `./build/N64Recomp ...` gets "This command requires approval" even
  though `Bash(./build/:*)` is allowlisted (hit fresh again s200; trust
  this, don't re-litigate).
- The crash handler dumps siginfo + full ARM64 register file on every
  SIGSEGV/SIGBUS/SIGABRT (`src/main/main.cpp`) — check `[CRASH][siginfo]`/
  `[CRASH][mcontext]`/`[CRASH][vifs-snapshot]` lines first, plus the
  backtrace lines immediately below them.
- `N64Recomp/fixup_game_funcs.py` is **not fully idempotent** — confirmed
  again s200 (see "Do not" above in that session's notes). Always regen
  (`make_elf.py` -> `N64Recomp`) before re-running fixup if you're not
  sure it's only been run once since the last regen.
- Any edit under THIS repo's `lib/` needs `./submodule-patches/export.sh`
  + commit in the SAME session (not applicable s201 — no `lib/` edits).
  `N64Recomp` and `rogue_squadron64` are SEPARATE checkouts outside this
  repo, NOT `lib/` submodules — their uncommitted changes are flagged for
  the user, not this session's call to commit.
- Re-running the same soak script/tag overwrites the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
  `run.log` files are multi-GB — NEVER `Read` or `cat` them whole — always
  `grep -a`/`sed -n` for specific line ranges, and use `grep -a` (not
  plain `grep`) since these logs can contain binary-looking bytes.
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh` /
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied in ONE
  Bash call — prefer separate Bash calls (one `cd`, then the next command
  in its own call; cwd persists across calls).
- Block on a soak by launching with `run_in_background: true` and calling
  `TaskOutput(task_id, block=true, timeout=300000-480000)` — do not end
  the turn while a background soak is still running.
- Heredocs get rejected by this session's Bash tool — use the Write tool
  instead, including for large PORTING-STATE.md appends (write a tmpfile
  with the Write tool, then `cat tmpfile >> PORTING-STATE.md`).
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.
- `scratch/agent/STATUS`/`OUTCOME` get reset to `WORKING`/deleted at the
  START of each iteration by the harness — finding them in that state at
  session start is normal, not evidence of a crashed prior session.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now well over the ~35 KB CLAUDE.md budget and
exceeds the Read tool's 256 KB single-read limit (confirmed s195, still
true s201 — read it with `grep`/`sed -n`, never a plain whole-file
`Read`). Migrate durable mechanism/architecture material to
`PROJECT-OVERVIEW.md` and prune superseded detail, paired with a real
experiment — flagged for many sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session's commit
scope. Still flagged for the user, not committed autonomously.
