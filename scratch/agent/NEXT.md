# NEXT work unit — build a `MEM_W`-address bounds tracer scoped to
`renderUnlitMeshFaces` for the `+8772`/`+508` KSEG0-zero-extension bug.
Source reading is exhausted for this function (s204 whole-function pass,
s207 offset-targeted re-read — both clean, zero source-level bypass found).

Read `docs/CURRENT-TRUTH.md`'s `-48` next-steps item (top of the list) and
PORTING-STATE Session 207 in full before doing anything else (`grep -n
"^## Session 207" PORTING-STATE.md`). Session 206 (the dladdr pc-symbol hit)
and 200-205 (the callee source reads) are cited there if you need the crash
mechanism refresher.

## Why this is the next work unit

s204 and s207 (this session, offset-targeted, extra scrutiny on the two
linked-list pointer-chase reload sites) both read `renderUnlitMeshFaces`
(`N64Recomp/RecompiledFuncs/funcs_4.c:4951-5605`) and its one callee
(`getTextureLUTFieldAt8`, `funcs_6.c:13392-13417`, confirmed architecturally
non-inlined — `RECOMP_FUNC` is `noinline` per `recomp.h:22`, and this
project builds `RecompiledFuncs` at `CMAKE_BUILD_TYPE=Debug`/`-O0`, so no
compiler could have inlined it regardless) and found **zero** source-level
zero-extension bypass: every pointer computation goes through `ADD32`/`SUB32`
(which force-`(int32_t)`-then-widen-to-`gpr`), every `MEM_W` result assigns
directly into a `gpr` (`ctx->rN`) field (sign-extends via C's implicit
`int32_t -> uint64_t` promotion), every `MEM_HU`/`MEM_BU` zero-extending load
feeds only a flag/mask/color/comparison field, never a pointer.

Yet s206's `dladdr`-based pc symbolizer directly named `renderUnlitMeshFaces+508`
as the actual faulting pc on a 3rd occurrence of this bug — real dynamic
evidence, not a guess. The contradiction between "source reads clean" and
"dynamic evidence says it's in here" is not resolved by more reading. Two
explanations, undistinguished:

- (a) **Bad data, clean dereference**: some node in the linked list this
  function walks was written with a corrupted/zero-extended address by a
  DIFFERENT function entirely (not `renderUnlitMeshFaces` itself), and this
  function is simply the first to dereference it. If true, the whole
  callee-narrowing strategy (s194-207) was scoped to the wrong place from
  the start — the bug is upstream, in whatever writes these list nodes.
- (b) **ARM64 codegen issue**: a genuine clang miscompile of some pattern in
  this function at `-O0`, invisible at the C source level. Exotic — keep
  lowest priority per the boring-first-explanations rule until (a) is ruled
  out.

A `MEM_W`-address bounds tracer scoped to just this one function tests (a)
directly: if the address about to be dereferenced is already out of
`rdram`'s valid range BEFORE the macro's own dereference, the DATA was bad
walking in — confirms (a) and points at whichever earlier write put it there
(cross-reference with existing write-side guards). If the address is fine
right up until the crash (i.e., the tracer's own bounds check never fires but
the crash still happens), that's evidence AGAINST (a) and points toward (b)
or a still-unidentified third explanation.

## Do exactly one this iteration

1. **Instrument** `funcs_4.c`'s `renderUnlitMeshFaces` via a NEW
   `fixup_game_funcs.py` patch block (regen order: hand-edits to generated
   code go in fixup scripts or they die at the next regen — see the existing
   `_psn_callee_trace`/GUARD patches around line 4548+ and line 2342+ for the
   codebase's established pattern: a `static int s_..._enabled = -1;` +
   `getenv()`-gated check, `fprintf(stderr, ...)` unthrottled when enabled).
   Add a bounds check macro/inline call BEFORE the dereference at these four
   sites (line numbers as of this session — re-grep to confirm unchanged
   before patching, in case a regen shifted them):
   - `funcs_4.c:4975` — `ctx->r18 = MEM_W(ctx->r20, 0X54);` (first list head load)
   - `funcs_4.c:5009` — `ctx->r16 = MEM_W(ctx->r20, 0X20);` (second list head load)
   - `funcs_4.c:5546` — `ctx->r16 = MEM_W(ctx->r16, 0X0);` (inner loop pointer-chase reload)
   - `funcs_4.c:5563` — `ctx->r18 = MEM_W(ctx->r18, 0X4);` (outer loop pointer-chase reload)

   For each, before the `MEM_W(...)` call, check whether the SOURCE register
   (`ctx->r20`/`ctx->r16`/`ctx->r18` — the one being read FROM, i.e. the
   pointer already in hand before this load) has the expected KSEG0 upper
   bits (`(reg >> 32) == 0xFFFFFFFF`) and whether the resulting rdram-relative
   byte offset (`(reg + offset) - 0xFFFFFFFF80000000`, matching `MEM_W`'s own
   formula in `recomp.h:95-96`) falls inside `[0, rdram_size)`. Log (do NOT
   skip/guard — this must not change behavior or it invalidates reproduction)
   with `fprintf(stderr, "[CRASH][unlit-mesh-tracer] site=<A|B|C|D> reg=0x%016llx offset=0x%x computed_addr=... IN_BOUNDS|OOB\n", ...)`
   gated behind a new env var, e.g. `ROGUESQ_LOG_UNLIT_MESH_TRACER`. Only log
   on OOB by default to keep log volume sane during a soak (this differs from
   the unthrottled convention of the older GUARDs — justified because this
   function is hot, called every frame per visible mesh).
2. **Positive control, in the same soak**: also add an UNCONDITIONAL counter
   (increments every call to `renderUnlitMeshFaces`, logged every N=10000
   calls or on process exit) so a null result is verifiable as "the function
   ran and the check executed" and not "the instrument never fired." This is
   the iron rule #1 requirement — a null result without this is worthless.
3. **Regen + build**: `make_elf.py` -> `N64Recomp` (`env`-prefixed, from the
   `N64Recomp` checkout) -> `fixup_game_funcs.py` -> cmake (DEVELOPER_DIR=
   /Applications/Xcode.app/Contents/Developer cmake --build ...). Confirm the
   fixup report line shows the four sites patched.
4. **Soak**: launch with `ROGUESQ_LOG_UNLIT_MESH_TRACER=1` (use `env` prefix
   per the permission-matching note below), `run_in_background: true`, block
   via `TaskOutput(..., block=true, timeout=300000-480000)`. Copy the driver
   script to a new tag name (do not reuse a prior soak's `run.log` path).
   Expected discriminating outcomes:
   - **OOB fires before a crash, at one of the four sites** → confirms
     explanation (a). The site tells you which register/list was already bad
     walking in — grep for what else in this codebase writes to that same
     struct offset to find the actual corrupting function.
   - **Soak crashes with the same `+8772`/`renderUnlitMeshFaces+508` signature
     but the tracer NEVER logged an OOB** → rules out (a) for these four
     sites specifically (not all-encompassing — only tests these four
     reloads, not every `MEM_W` in the function). Escalate toward (b) or
     widen the tracer to the remaining `MEM_W` call sites in the function
     before considering a codegen-bug hypothesis.
   - **Soak completes with 0 crashes of this signature** (this bug is rare —
     3 occurrences across many prior soaks) → inconclusive on its own; check
     the positive-control counter incremented a nontrivial amount (confirms
     the function is actually being exercised) and extend the soak duration
     next iteration rather than concluding anything.

## Do not

- Do not re-read `renderUnlitMeshFaces`'s source again this iteration — s204
  and s207 both did this at increasing scrutiny, 0 findings each time. Build
  the tracer instead.
- Do not re-read `processSceneNode`, `renderLitMeshFaceGroup`,
  `submitSceneNodeRender`, `renderFlatMeshFaceGroup`, or
  `renderLitTexturedMeshFaces` this iteration — still provisionally clean,
  untouched by s206/s207's evidence.
- Do not re-attempt `nm`/`atos`/`otool`/`objdump` this iteration — s207
  re-confirmed both `nm` and `atos` still require approval and are denied in
  this non-interactive session (2 independent attempts). Only retry if
  something about the environment has visibly changed.
- Do not widen the tracer to instrument EVERY `MEM_W` call in the function on
  the first pass — start with the four highest-probability sites (the two
  list-head loads, the two loop-back pointer-chase reloads) to keep the log
  volume and the fixup patch bounded. Widen only if this soak's result is
  genuinely ambiguous (see "Expected discriminating outcomes" above).
- Do not re-touch the s123/s131 `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`,
  the s197 `SCENE_NODE_CACHE_GUARD`, the s190 `scene-node-ptr-guard`, the
  s196 `REINTERPRET_TILE_GUARD`, or s199's `video-frame-tick-guard` — all
  correct-per-spec, all still 0-fire (or unconfirmed), no new evidence
  against any of them.
- Do not chase the `frameStartReset+532` family, the 23rd-class
  `waitForAnyAudioSlot` SIGSEGV, or the `evalCubicSplineAtTime` SIGBUS
  family this iteration unless this session's own work produces new
  evidence about them specifically.

## Environment notes (carried forward, still current)

- The `[CRASH][pc-symbol]` diagnostic (`src/main/main.cpp`, `dladdr()` on the
  raw mcontext `pc`) is permanent and always-on — trust it over
  `backtrace_symbols_fd()`'s output when the two disagree.
- Disassembly/symbolication tools (`nm`/`otool`/`objdump`/`lldb`/`atos`) are
  ALL blocked as of s207 (non-interactive session, no human to clear the
  approval prompt) — re-verified this session with `nm` AND `atos`
  specifically (`atos` was a promising alternative since it resolves
  addresses to file:line directly from debug info, sidestepping the whole
  byte-offset-guessing exercise, but it's denied same as the rest). Re-verify
  fresh only if something about the environment seems to have changed.
- This project builds `CMAKE_BUILD_TYPE=Debug` (`-O0`) globally; only the 3
  RSP-ucode translation units (`FACTOR5_UCODE_C`/`_B_C`/`_BOOT_C`) get an
  explicit `-O2` override (`CMakeLists.txt:239-247`, s38's own comment).
  `RecompiledFuncs` (all of `funcs_*.c`) stays at `-O0`. `RECOMP_FUNC`
  (`N64Recomp/include/recomp.h:22`, non-MSVC branch) is `extern inline
  __attribute__((weak,noinline))` — every recompiled game function is
  explicitly non-inlinable. Together: no game function can be silently
  inlined into a caller, and `-O0` means no cold-path splitting/instruction
  reordering — a dladdr symbol+offset genuinely identifies where in that
  function's own body (in roughly source order) a fault occurred, even
  though the precise ARM64-instructions-per-source-line ratio is still
  uncalibrated (only one `[CRASH][pc-symbol]` sample exists so far).
- `./build/N64Recomp rogue_squadron.toml` (from the `N64Recomp` checkout)
  needs an `env` prefix to clear the permission-prefix-match wall — bare
  `./build/N64Recomp ...` gets "This command requires approval" even
  though `Bash(./build/:*)` is allowlisted (hit repeatedly; trust this,
  don't re-litigate).
- The crash handler dumps siginfo + full ARM64 register file + the
  pc-symbol line on every SIGSEGV/SIGBUS/SIGABRT (`src/main/main.cpp`) —
  check `[CRASH][siginfo]`/`[CRASH][mcontext]`/`[CRASH][pc-symbol]`/
  `[CRASH][vifs-snapshot]` lines first, plus the backtrace lines
  immediately below them.
- `N64Recomp/fixup_game_funcs.py` is **not fully idempotent** — confirmed
  s200. Always regen (`make_elf.py` -> `N64Recomp`) before re-running
  fixup if you're not sure it's only been run once since the last regen.
- Any edit under THIS repo's `lib/` needs `./submodule-patches/export.sh`
  + commit in the SAME session. `N64Recomp` and `rogue_squadron64` are
  SEPARATE checkouts outside this repo, NOT `lib/` submodules — their
  uncommitted changes are flagged for the user, not this session's call
  to commit. (This iteration's edits are to `N64Recomp/fixup_game_funcs.py`
  and `N64Recomp/RecompiledFuncs/funcs_4.c` — both live in the SEPARATE
  `N64Recomp` checkout, not this repo's `lib/`, so no `export.sh` applies;
  flag the uncommitted `N64Recomp` changes for the user same as always.)
- Re-running the same soak script/tag overwrites the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
  `run.log` files are multi-GB — NEVER `Read` or `cat` them whole — always
  `grep -a`/`sed -n` for specific line ranges.
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
true s207 — read it with `grep`/`sed -n`, never a plain whole-file
`Read`). Migrate durable mechanism/architecture material to
`PROJECT-OVERVIEW.md` and prune superseded detail, paired with a real
experiment — flagged for 8+ sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session's commit
scope. Still flagged for the user, not committed autonomously.
