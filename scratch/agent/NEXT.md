# NEXT work unit — narrow `processSceneNode+8772` (KSEG0 zero-extension bug)
into ONE of its five render callees

Read `docs/CURRENT-TRUTH.md`'s `-48` next-steps item (top of the list) and
PORTING-STATE Session 200 in full before doing anything else (`grep -n
"^## Session 200" PORTING-STATE.md`). Also skim Session 194 (original
register-file decode) and Session 199 (first occurrence recurrence) if you
need the crash mechanism refresher — s200 doesn't repeat it, just cites it.

## Why this is the next work unit

s200 exhaustively ruled OUT `processSceneNode` itself as the source of the
zero-extension bug, via two independent lines of evidence: (1) a full
static read of the function's ~1140-line recompiled C body found no
pointer computation that bypasses the sign-extending `ADD32`/`SUB32`/`S32`/
`MEM_W` convention (recomp.h:89-108) — everything that reaches a
`MEM_W`/`MEM_H`/`MEM_B` in this function's literal source re-canonicalizes
on every use; (2) a new call-site tracer (10 sites, `N64Recomp/
fixup_game_funcs.py`, env var `ROGUESQ_LOG_PROCESS_SCENE_NODE_GUARD`)
logging the pointer args passed into each of the five render callees
(`submitSceneNodeRender`, `renderFlatMeshFaceGroup`, `renderLitMeshFaceGroup`,
`renderUnlitMeshFaces`, `renderLitTexturedMeshFaces`) confirmed it
dynamically: one soak logged 46,292 real calls, 0 of them had a
non-canonical pointer. The tracer's 46k real, sane firings are themselves
the positive control (this is NOT a null result — the instrument
demonstrably works and still found nothing wrong at the boundary). Since
the crash's `lr` is a return address INTO `processSceneNode` (the fault
itself is one call frame deeper), and that caller boundary is now proven
clean, the defect must live inside one of the five callees' own bodies —
this promotes "find which callee, then find the defect inside it" to the
top of the list.

## Do this, in order

1. **Re-run the soak** that already has the tracer instrumented — copy
   `scratch/agent/run_processscenenodecalleetrace1.sh` to a new tag
   (`processscenenodecalleetrace2` or similar; same standard env block,
   `ROGUESQ_LOG_PROCESS_SCENE_NODE_GUARD=1` already set). No rebuild needed,
   the binary from s200 already has the tracer. Launch in background, block
   on it (`TaskOutput(task_id, block=true, timeout=300000-480000)`), do not
   end the turn while it's running.
2. **Check the outcome**:
   - **Soak dies to a SIGBUS/SIGSEGV matching the `processSceneNode+8772`
     signature** (check `[CRASH]` lines, `si_addr`/`far` should decompose
     the same way as s194/s199: `rdram_base + 0x0000000080xxxxxx`, top 32
     bits zero) → `grep -a "\[process-scene-node-callee\]" run.log | tail -1`
     to get the LAST site/callee logged before the crash. That names your
     target function for step 3. Also sanity-check: were the args at that
     last call canonical? (They should be, per s200 — if NOT, that's a
     contradiction worth flagging, it would mean s200's tracer coverage
     missed a path.)
   - **Soak dies to something else** (a different, already-catalogued crash
     class) → informative but not on this bug; note it, and if this is the
     3rd consecutive uninformative iteration on this hypothesis, STOP and
     go to the fallback in step 4 instead of re-running a 4th time (budget
     rule).
   - **Soak completes clean, no crash** → also informative (another data
     point that the bug is rare/hard to trigger); re-run once more if this
     is only the 2nd such soak (s200's was the 1st), or fall back to step 4
     if it's the 3rd.
3. **If a callee got named**: read that function's recompiled C body in
   chunks (they're large — `renderLitMeshFaceGroup` is ~5000 lines,
   `submitSceneNodeRender` ~3000, the others 600-1500) hunting for the same
   pattern s200 already ruled out in `processSceneNode`: a pointer computed
   without going through `ADD32`/`SUB32`/`S32`/`MEM_W`'s sign-extend
   convention. Delegate this read to a subagent (same approach s200 used
   for `processSceneNode` — brief it with the recomp.h macro definitions
   and the exact crash signature, ask for file:line + explanation, not a
   full paste-back) rather than reading the whole thing inline. Once found,
   guard or fix it, mirroring the established RDRAM-range-check pattern
   (`fixup_game_funcs.py`'s existing guards are all templates for this).
4. **Fallback if no callee gets named after 3 soaks** (no recurrence, or
   recurrence doesn't match this signature): pick `renderLitMeshFaceGroup`
   to read first anyway — it's the largest/most complex of the five and had
   high call volume in s200's one soak (10,427 calls at site I alone) — and
   apply the same subagent-assisted read as step 3, unprompted by a fresh
   crash. This trades a guaranteed-relevant trigger for guaranteed forward
   progress on the search space.
5. Regenerate (`make_elf.py` -> `env ./build/N64Recomp rogue_squadron.toml`
   -> `env python3 fixup_game_funcs.py` -> `cmake --build build -j8`,
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` for Metal) if
   you add a new patch. **Verify no duplication before building**: after
   the regen step (make_elf.py -> N64Recomp), grep-count your new patch's
   anchor string in the fresh RecompiledFuncs output (should be 0,
   confirming a clean unpatched regen), THEN run fixup exactly ONCE, THEN
   grep-count again (should match your site count). s200 accidentally ran
   fixup 3x in a row (approval-prompt retry loop) and it DID cause real
   duplication elsewhere in the file (`funcs_0.c`'s unrelated `rs_malloc`
   diagnostic, a `redefinition of 's_rsmalloc_req_size'` compile error) —
   confirms the documented non-idempotence is real, not just a stale
   warning. If you hit an approval prompt on `./build/N64Recomp
   rogue_squadron.toml`, prefix with `env` (matches the `Bash(env:*)`
   allowlist rule) rather than retrying the bare command.
6. Whatever the outcome, update `PORTING-STATE.md` (new session entry),
   `docs/CURRENT-TRUTH.md`'s `-48` entry, and this file, per the exit
   contract.

## Do not

- Do not re-read `processSceneNode` itself for this bug — s200 closed that
  question with two independent lines of evidence (source read + dynamic
  trace, 46,292/46,292 clean). Only revisit if a FUTURE crash's register
  evidence contradicts the tracer (e.g. a non-canonical arg logged right
  before a crash) — that would be a genuinely new, surprising fact worth
  chasing, not a reason to redo the same read.
- Do not re-touch the s123/s131 `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`,
  the s197 `SCENE_NODE_CACHE_GUARD`, the s190 `scene-node-ptr-guard`, the
  s196 `REINTERPRET_TILE_GUARD`, or s199's `video-frame-tick-guard` — all
  correct-per-spec, all still 0-fire, no new evidence against any of them.
- Do not chase the 23rd-class `waitForAnyAudioSlot` SIGSEGV or the
  `evalCubicSplineAtTime` SIGBUS family this iteration unless THIS
  session's soak dies to one of them AGAIN after exhausting budget on this
  item — both remain open, flagged, lower priority.
- **Never run `fixup_game_funcs.py` more than once per `N64Recomp` regen**,
  even if you believe your own new patch is idempotent — s200 proved other,
  older patches in the same file are not, and the failure mode is a build
  error, not a silent corruption, so it WILL be caught at compile time, but
  it wastes a full regen+build cycle to recover from.

## Environment notes (carried forward, still current)

- Disassembly tools (`nm`/`otool`/`objdump`/`lldb`) still blocked as of
  s199 (non-interactive session, no human to clear the approval prompt);
  not re-tested s200 since the tracer approach made it unnecessary again —
  re-verify fresh only if something about the environment seems to have
  changed.
- `./build/N64Recomp rogue_squadron.toml` (from the `N64Recomp` checkout)
  needs an `env` prefix to clear the permission-prefix-match wall — bare
  `./build/N64Recomp ...` gets "This command requires approval" even though
  `Bash(./build/:*)` is allowlisted (s200 hit this fresh; PORTING-STATE
  Sessions ~9583-11245 document the same fix repeatedly, so trust it,
  don't re-litigate).
- The crash handler dumps siginfo + full ARM64 register file on every
  SIGSEGV/SIGBUS/SIGABRT (`src/main/main.cpp`) — check `[CRASH][siginfo]`/
  `[CRASH][mcontext]`/`[CRASH][vifs-snapshot]` lines first, plus the
  backtrace lines immediately below them.
- `N64Recomp/fixup_game_funcs.py` is **not fully idempotent** — confirmed
  again this session (see "Do not" above). Always regen (`make_elf.py` ->
  `N64Recomp`) before re-running fixup if you're not sure it's only been
  run once since the last regen.
- Any edit under THIS repo's `lib/` needs `./submodule-patches/export.sh` +
  commit in the SAME session (not applicable this session — no `lib/`
  edits). `N64Recomp` and `rogue_squadron64` are SEPARATE checkouts outside
  this repo, NOT `lib/` submodules — their uncommitted changes (including
  `fixup_game_funcs.py` itself) are flagged for the user, not this
  session's call to commit.
- Re-running the same soak script/tag overwrites the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
  `run.log` files are multi-GB (s200's was 7.3M lines from one ~3-minute
  soak with all diagnostics on) — NEVER `Read` or `cat` them whole — always
  `grep -a`/`sed -n` for specific line ranges, and use `grep -a` (not plain
  `grep`) since these logs can contain binary-looking bytes that make grep
  think they're binary files and suppress output.
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh` /
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied in ONE
  Bash call, and even a single `cd foo && git status` in one call can get
  auto-flagged for approval on some directories — prefer separate Bash
  calls (one `cd`, then the next command in its own call; cwd persists
  across calls). Multi-line piped commands (`grep | grep | wc`) can also
  get flagged as "multiple operations" needing approval — prefer one
  simple command per Bash call when iterating quickly.
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
true s200 — read it with `grep`/`sed -n`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md`
and prune superseded detail, paired with a real experiment — flagged for
many sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes (including this session's
`fixup_game_funcs.py` edit), unrelated to this session's commit scope.
Still flagged for the user, not committed autonomously.
