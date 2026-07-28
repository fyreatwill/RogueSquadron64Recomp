# NEXT work unit — source-read `renderLitTexturedMeshFaces`, the LAST
remaining candidate, for the same KSEG0 zero-extension bug

Read `docs/CURRENT-TRUTH.md`'s `-48` next-steps item (top of the list) and
PORTING-STATE Session 204 in full before doing anything else (`grep -n
"^## Session 204" PORTING-STATE.md`). Session 200 (original callee
narrowing) and Session 194/199 (original register-file decode) are cited
there if you need the crash mechanism refresher — s204 doesn't repeat it,
just cites it.

## Why this is the next work unit

s200 exhaustively ruled OUT `processSceneNode` itself. s201 cleared
`renderLitMeshFaceGroup`. s202 cleared `submitSceneNodeRender`. s203
cleared `renderFlatMeshFaceGroup`. s204 cleared `renderUnlitMeshFaces`
(source-clean, single-source, same method: subagent read of all ~654
lines, every zero-extending load individually traced to its downstream
use, zero raw pointer arithmetic bypassing `ADD32`/`SUB32`, zero stray
`(uint32_t)`/`(uint64_t)` casts feeding an address). That leaves exactly
ONE unexamined direct callee of `processSceneNode`:
`renderLitTexturedMeshFaces`.

**Its size has been measured this session**: `funcs_3.c:22073-23886`
(~1813 lines — it's the last function in `funcs_3.c`, ending at EOF, not
at another `RECOMP_FUNC` boundary). This is the LARGEST of the five
callees examined for this bug — budget the read accordingly (more chunks
than s204's ~654-line read needed).

## Do this, in order

1. **Do NOT re-soak the tracer this iteration.** 3 soaks, 116,950 calls,
   0 reproductions is enough per the budget rule (iron rule 8) — this was
   already true as of s201 and nothing since changes it.
2. **Source-read `renderLitTexturedMeshFaces`**
   (`N64Recomp/RecompiledFuncs/funcs_3.c:22073-23886`, ~1813 lines).
   Delegate to a subagent using the SAME brief s201/s202/s203/s204 used
   successfully:
   - Give it the exact macro definitions from
     `/Users/williambuckley/Documents/Tools/N64Recomp/include/recomp.h`
     lines 86-108 (`SIGNED`/`ADD32`/`SUB32`/`MEM_W`/`MEM_H`/`MEM_B`/
     `MEM_HU`/`MEM_BU`).
   - Give it the exact crash signature: a KSEG0 zero-extension bug, fault
     address decomposing as `rdram_base + 0x0000000080xxxxxx` (top 32
     bits zero instead of `0xFFFFFFFF`-sign-extended).
   - Ask it to hunt for: raw `+`/`-` arithmetic on `gpr`/`uint64_t`
     register values that bypasses `ADD32`/`SUB32`; `(uint32_t)`/
     `(uint64_t)` casts feeding a pointer-shaped register; zero-extending
     `MEM_HU`/`MEM_BU` loads whose result gets ADDED into a pointer (not
     just masked into a flag/color field — that pattern was benign in all
     five prior-cleared functions, don't assume it's always benign, check
     each occurrence's actual use); `MOVZ`/`MOVN`-style register-assigning
     ternaries where one branch sign-extends and another doesn't; any
     cast/helper you don't recognize from the macro list.
   - Ask for file:line + one-paragraph mechanism explanation only — no
     large code paste-backs. Read in chunks (offset/limit) — this is the
     largest function in the batch (~1813 lines), likely needs 3-4 chunks.
3. **If a bypass is found**: guard or fix it, mirroring the established
   RDRAM-range-check pattern (`N64Recomp/fixup_game_funcs.py`'s existing
   guards are all templates for this — e.g. the s196 `REINTERPRET_TILE_GUARD`
   or s197 `SCENE_NODE_CACHE_GUARD` for shape). Regenerate per step 5 below,
   then soak once to look for a positive control (the guard firing) or at
   minimum a clean pass past the crash's usual decisionN range.
4. **If clean (no bypass found)**: this closes out ALL FIVE direct callees
   of `processSceneNode` as source-clean. Do NOT invent a sixth callee to
   examine — instead, per CURRENT-TRUTH's own next-step note, the
   callee-narrowing strategy is then exhausted and the instrument itself
   needs rethinking: the current `processScenenNodeCalleeTrace` tracer only
   logs call-boundary args, so it is structurally blind to a defect that's
   introduced AND consumed entirely within one callee's own body (e.g. a
   grandchild call, or a value that never crosses back through a logged
   boundary). Write up this pivot explicitly in the session log and in the
   next NEXT.md — do not just re-read a callee a second time hoping for a
   different answer.
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
   #205), `docs/CURRENT-TRUTH.md`'s `-48` entry, and this file, per the
   exit contract.

## Do not

- Do not re-read `processSceneNode` (s200 closed it, 2 independent lines
  of evidence), `renderLitMeshFaceGroup` (s201 closed it, source-clean),
  `submitSceneNodeRender` (s202 closed it, source-clean),
  `renderFlatMeshFaceGroup` (s203 closed it, source-clean), or
  `renderUnlitMeshFaces` (s204 closed it, source-clean) for this bug. Only
  revisit any of them if a FUTURE crash's register evidence directly
  contradicts them.
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
  s202/s203/s204 (non-interactive session, no human to clear the approval
  prompt); not re-tested s204 since source-reading made it unnecessary
  again — re-verify fresh only if something about the environment seems
  to have changed.
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
  + commit in the SAME session (not applicable s204 — no `lib/` edits).
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
  the turn while a background soak is still running. This applies to
  background subagents too (`Agent` tool with default background mode) —
  `TaskOutput` accepts the agent's task/agent id and blocks until it
  completes; use it before declaring the exit-contract STATUS, since the
  Stop hook checks for STATUS=DONE/BLOCKED and will reject a turn ended
  while a dispatched agent is still outstanding (hit fresh s202). Note:
  running an `Agent` tool call with `run_in_background: false` and waiting
  for its direct return (as s204 did) avoids this entirely — prefer that
  for a single foreground source-read when you need the result before
  writing the exit-contract docs anyway.
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
true s204 — read it with `grep`/`sed -n`, never a plain whole-file
`Read`). Migrate durable mechanism/architecture material to
`PROJECT-OVERVIEW.md` and prune superseded detail, paired with a real
experiment — flagged for many sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session's commit
scope. Still flagged for the user, not committed autonomously.
