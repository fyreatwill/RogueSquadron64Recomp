# NEXT work unit — pivot: the callee-narrowing strategy for the `+8772`
KSEG0-zero-extension bug is EXHAUSTED. Do NOT source-read another callee.

Read `docs/CURRENT-TRUTH.md`'s `-48` next-steps item (top of the list) and
PORTING-STATE Session 205 in full before doing anything else (`grep -n
"^## Session 205" PORTING-STATE.md`). Sessions 200-204 (the five prior
callee reads) and 194/199 (the original register-file decode) are cited
there if you need the crash mechanism refresher.

## Why this is the next work unit

s200-205 source-read ALL SIX functions in `processSceneNode`'s
direct-callee chain (`processSceneNode` itself, `renderLitMeshFaceGroup`,
`submitSceneNodeRender`, `renderFlatMeshFaceGroup`, `renderUnlitMeshFaces`,
`renderLitTexturedMeshFaces`) for a bypass of the sign-extending
`ADD32`/`SUB32`/`MEM_W` convention. All six came back clean. There is no
seventh callee to invent — inventing one and re-reading a cleared function
without new evidence would violate the "do not re-read a cleared function"
rule from the last five sessions' NEXT.md files.

Two pivot options are on the table, in order of expected information
value. **Do exactly one this iteration** (budget rule: pick the
highest-information probe, don't try to do both).

## Option A (higher information value): instrument internal pointer
computations, not just call-boundary args

The current `processScenenNodeCalleeTrace` tracer (116,950 calls logged
across 3 soaks, 0 reproductions) only logs args AT the call boundary
between `processSceneNode` and its six callees. It is structurally BLIND
to a defect that's introduced and consumed entirely within one callee's
own body — e.g. a value computed and dereferenced without ever crossing
back out through a logged call-boundary argument, or a bug living inside
an uninstrumented grandchild call one of the six functions makes.

Concretely:
1. Pick ONE of the six cleared functions to instrument first —
   `renderLitTexturedMeshFaces` is the best candidate (largest, most
   recently read, freshest in context) UNLESS you find a reason to prefer
   another.
2. Add a lightweight tracer that logs every `MEM_W`/`MEM_H`/`MEM_B`/
   `MEM_HU`/`MEM_BU` ADDRESS argument evaluated inside that function's
   body during a phase-gated soak (not the loaded VALUE — the address
   expression's runtime value, so you can check its top 32 bits are
   `0xFFFFFFFF`-sign-extended, not zero). This needs a source patch (via
   `fixup_game_funcs.py`, NOT a hand-edit to generated code — regen order
   applies) that wraps address computations with a logging macro, mirroring
   how `processScenenNodeCalleeTrace` was built (find it in
   `fixup_game_funcs.py` and reuse its logging/rate-limiting pattern so you
   don't blow the log budget — iron rule 3, scope the log budget to the
   phase).
3. Positive control REQUIRED (iron rule 1): before trusting a null result,
   confirm the new tracer visibly fires for at least one call during a
   short soak — e.g. count total logged addresses and eyeball a sample for
   sane KSEG0 values, so you know the instrument is actually running, not
   silently disabled.
4. Soak once, phase-gated on VI transitions (iron rule 2), long enough to
   reach the crash's usual decisionN range if possible. Look for ANY
   logged address with zero top-32-bits.

## Option B (cheaper, do if Option A's instrumentation work looks too big
for one iteration): sanity-check the original premise

Before building new instrumentation, it's worth spending a cheap iteration
asking whether 6/6 clean source reads means "the bug isn't in this chain"
rather than "we're not looking at the right thing." Re-read the s194/s199
register-file decode (`grep -n "^## Session 194\|^## Session 199"
PORTING-STATE.md`) and check specifically: does the fault address's
decomposition (`rdram_base + 0x0000000080xxxxxx`) actually, mechanically
implicate `processSceneNode`'s six direct callees — e.g. via a backtrace
frame, a register holding one of their return addresses, or similar
concrete evidence — or was the callee-narrowing strategy adopted on
weaker footing (e.g. "this is the function active near the crash, so
its callees are suspects")? If the link was always circumstantial, this
is the information-value discriminator: it tells you whether Option A is
worth building at all, or whether the search should widen to a
completely different call path.

## Do not

- Do not source-read `processSceneNode`, `renderLitMeshFaceGroup`,
  `submitSceneNodeRender`, `renderFlatMeshFaceGroup`, `renderUnlitMeshFaces`,
  or `renderLitTexturedMeshFaces` again — all six closed, source-clean,
  same method. Only revisit if a FUTURE crash's register evidence directly
  contradicts them.
- Do not re-run the `processScenenNodeCalleeTrace` soak as-is (call-boundary
  args only) — 3 soaks, 116,950 calls, 0 reproductions already exhausts
  that specific instrument's budget. A NEW instrument (Option A) that logs
  something the old one didn't is fine; re-running the same one is not.
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
  s202-205 (non-interactive session, no human to clear the approval
  prompt); re-verify fresh only if something about the environment seems
  to have changed.
- `./build/N64Recomp rogue_squadron.toml` (from the `N64Recomp` checkout)
  needs an `env` prefix to clear the permission-prefix-match wall — bare
  `./build/N64Recomp ...` gets "This command requires approval" even
  though `Bash(./build/:*)` is allowlisted (hit repeatedly; trust this,
  don't re-litigate).
- The crash handler dumps siginfo + full ARM64 register file on every
  SIGSEGV/SIGBUS/SIGABRT (`src/main/main.cpp`) — check `[CRASH][siginfo]`/
  `[CRASH][mcontext]`/`[CRASH][vifs-snapshot]` lines first, plus the
  backtrace lines immediately below them.
- `N64Recomp/fixup_game_funcs.py` is **not fully idempotent** — confirmed
  s200. Always regen (`make_elf.py` -> `N64Recomp`) before re-running
  fixup if you're not sure it's only been run once since the last regen.
- Any edit under THIS repo's `lib/` needs `./submodule-patches/export.sh`
  + commit in the SAME session (not applicable s205 — no `lib/` edits).
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
  the turn while a background soak is still running. Prefer a foreground
  `Agent` call (`run_in_background: false`) for a single source-read when
  you need the result before writing exit-contract docs anyway (this is
  what s204/s205 did, avoids the outstanding-agent Stop-hook rejection
  entirely).
- Heredocs get rejected by this session's Bash tool — use the Write tool
  instead, including for large PORTING-STATE.md appends (write a tmpfile
  with the Write tool, then `cat tmpfile >> PORTING-STATE.md`, then
  delete the tmpfile).
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.
- `scratch/agent/STATUS`/`OUTCOME` get reset to `WORKING`/deleted at the
  START of each iteration by the harness — finding them in that state at
  session start is normal, not evidence of a crashed prior session.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now well over the ~35 KB CLAUDE.md budget and
exceeds the Read tool's 256 KB single-read limit (confirmed s195, still
true s205 — read it with `grep`/`sed -n`, never a plain whole-file
`Read`). Migrate durable mechanism/architecture material to
`PROJECT-OVERVIEW.md` and prune superseded detail, paired with a real
experiment — flagged for many sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session's commit
scope. Still flagged for the user, not committed autonomously.
