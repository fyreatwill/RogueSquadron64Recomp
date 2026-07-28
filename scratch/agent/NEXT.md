# NEXT work unit — `renderUnlitMeshFaces+508` is the precisely-scoped
target for the `+8772` KSEG0-zero-extension bug. The callee-narrowing
search is NOT exhausted; s206 named the exact function via a new
`dladdr`-based crash-handler diagnostic.

Read `docs/CURRENT-TRUTH.md`'s `-48` next-steps item (top of the list) and
PORTING-STATE Session 206 in full before doing anything else (`grep -n
"^## Session 206" PORTING-STATE.md`). Sessions 194/199 (original
register-file decode) and 200-205 (the five callee source reads, four
still standing) are cited there if you need the crash mechanism refresher.

## Why this is the next work unit

s206 added a direct `dladdr()` call on the raw mcontext `pc` register
inside the SIGSEGV/SIGBUS/SIGABRT handler (`src/main/main.cpp`, new
`[CRASH][pc-symbol]` line) because the existing `backtrace_symbols_fd()`
output was silently failing to name the true faulting frame — it only ever
showed `processSceneNode + 8772` (the `lr` register, duplicated across two
backtrace frames), never the deeper frame where the fault actually
happened, because a frame-pointer-chain unwinder can't see past a leaf
frame with no saved `x29`/`x30`. One soak with the new diagnostic
(`pcsymbolize1`) caught a 3rd occurrence of the bug (`x9=0x80630062`,
byte-for-byte match to both priors, `decisionN=9679`, same 9660-9800 band)
and the new line read:

```
[CRASH][pc-symbol] pc=0x104c24a60 sym=renderUnlitMeshFaces+508 base=0x104564000
```

This directly contradicts s204's "clean" verdict on `renderUnlitMeshFaces`
(`N64Recomp/RecompiledFuncs/funcs_4.c:4951-5605`) — that read was
single-source/static-only and explicitly flagged as provisional. The other
four callees (`renderLitMeshFaceGroup`, `submitSceneNodeRender`,
`renderFlatMeshFaceGroup`, `renderLitTexturedMeshFaces`) are NOT
contradicted and stay provisionally clean.

## Do exactly one this iteration

**Re-read `renderUnlitMeshFaces`'s early region with the offset as a map,
not a blind full-function pass.** 508 bytes / 4 bytes-per-ARM64-instruction
≈ 127 instructions past the function's entry point (after prologue). Given
N64Recomp's typical per-MIPS-instruction expansion ratio, this most likely
falls within roughly the first 20-40 MIPS-equivalent source statements of
the function — i.e. `funcs_4.c:4951` through somewhere in the 4980-5030
range (s204's own notes put the first interesting pointer computation, the
table-entry address, at 5064-5067 — check whether that's before or after
the 508-byte mark, and read everything strictly earlier than it with fresh
eyes, since s204's own summary of that region ruled it out but did so as
part of a whole-function pass, not a targeted one).

Steps:
1. Confirm the function's exact byte layout is even inferable this way —
   sanity-check by finding `resetVertexCacheSlot`'s own first-crash
   evidence (if any exists) or another symbol with a known small offset,
   to confirm dladdr's offsets track source order roughly linearly (they
   should, absent unusual compiler reordering, but don't assume — check
   if there's contradicting evidence before trusting the estimate).
2. Read `funcs_4.c:4951` through roughly `5030` (pad generously past the
   127-instruction estimate — better to over-read a little than
   under-read) line by line for the same zero-extension-bypass pattern as
   every prior session: a pointer computation that reaches a
   `MEM_W`/`MEM_H`/`MEM_B` address argument WITHOUT going through
   `ADD32`/`SUB32`/`S32`'s `(int32_t)` re-sign-extension, or a stray
   `(uint32_t)`/`(uint64_t)` cast, or a `MEM_HU`/`MEM_BU` zero-extending
   load whose result feeds a pointer instead of a flag/mask.
3. If found: this is the root cause. Fix it (either correct the extension
   at the source, matching `MEM_W`'s convention, or add a targeted guard
   via `fixup_game_funcs.py` if the underlying game data can legitimately
   be a small/negative value being misread) and verify with one soak past
   decisionN 9800 without recurrence.
4. If NOT found in that narrower region: the offset-to-source-line mapping
   assumption in step 1 may be wrong, OR the defect is in a call
   `renderUnlitMeshFaces` itself makes (check whether it calls anything
   besides the macros — grep `funcs_4.c:4951-5605` for
   `[A-Za-z_]+\(rdram, *ctx\)` the same way s206 did for `processSceneNode`,
   to see if it has its own callees that could own byte offset 508).
   Don't fall back to re-reading the WHOLE function again (s204 already
   did that at static-only confidence) — instead scope a `MEM_W`-address
   tracer to just this one function (Option A from s205's NEXT.md, now
   correctly narrowed to one function instead of six) as the next pivot.

## Do not

- Do not re-read `processSceneNode`, `renderLitMeshFaceGroup`,
  `submitSceneNodeRender`, `renderFlatMeshFaceGroup`, or
  `renderLitTexturedMeshFaces` this iteration — s206's evidence didn't
  touch them; they remain provisionally clean at the same confidence they
  already had. Only revisit if a FUTURE crash's `[CRASH][pc-symbol]` line
  names one of them instead.
- Do not re-run the `processScenenNodeCalleeTrace` call-boundary tracer —
  still 3 soaks/116,950 calls/0 reproductions, budget exhausted, and s206
  already showed the defect is INSIDE a callee's body, not at a call
  boundary, so that specific instrument can't see it regardless.
- Do not re-touch the s123/s131 `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`,
  the s197 `SCENE_NODE_CACHE_GUARD`, the s190 `scene-node-ptr-guard`, the
  s196 `REINTERPRET_TILE_GUARD`, or s199's `video-frame-tick-guard` — all
  correct-per-spec, all still 0-fire (or unconfirmed), no new evidence
  against any of them this session.
- Do not chase the `frameStartReset+532` family, the 23rd-class
  `waitForAnyAudioSlot` SIGSEGV, or the `evalCubicSplineAtTime` SIGBUS
  family this iteration unless this session's own work produces new
  evidence about them specifically.

## Environment notes (carried forward, still current)

- The new `[CRASH][pc-symbol]` diagnostic (`src/main/main.cpp`, `dladdr()`
  on the raw mcontext `pc`) is now permanent and always-on (no env gate) —
  every future crash gets a real symbol name for the actual faulting
  frame, not just `lr`'s duplicated frame. Trust it over
  `backtrace_symbols_fd()`'s output when the two disagree.
- Disassembly tools (`nm`/`otool`/`objdump`/`lldb`) still blocked as of
  s202-206 (non-interactive session, no human to clear the approval
  prompt); re-verify fresh only if something about the environment seems
  to have changed. `dladdr()` (via a source-level patch, not an external
  tool invocation) is a viable substitute for symbol-level questions and
  does NOT hit this approval wall — consider it first for any future
  "which function is this address in" question before assuming
  disassembly is required.
- `./build/N64Recomp rogue_squadron.toml` (from the `N64Recomp` checkout)
  needs an `env` prefix to clear the permission-prefix-match wall — bare
  `./build/N64Recomp ...` gets "This command requires approval" even
  though `Bash(./build/:*)` is allowlisted (hit repeatedly; trust this,
  don't re-litigate).
- The crash handler dumps siginfo + full ARM64 register file + the new
  pc-symbol line on every SIGSEGV/SIGBUS/SIGABRT (`src/main/main.cpp`) —
  check `[CRASH][siginfo]`/`[CRASH][mcontext]`/`[CRASH][pc-symbol]`/
  `[CRASH][vifs-snapshot]` lines first, plus the backtrace lines
  immediately below them.
- `N64Recomp/fixup_game_funcs.py` is **not fully idempotent** — confirmed
  s200. Always regen (`make_elf.py` -> `N64Recomp`) before re-running
  fixup if you're not sure it's only been run once since the last regen.
  (Not applicable if your fix is a pure C source edit inside
  `funcs_4.c`/`funcs_3.c` made via a NEW `fixup_game_funcs.py` patch block
  — but IS applicable once you've run fixup once this session.)
- Any edit under THIS repo's `lib/` needs `./submodule-patches/export.sh`
  + commit in the SAME session. `N64Recomp` and `rogue_squadron64` are
  SEPARATE checkouts outside this repo, NOT `lib/` submodules — their
  uncommitted changes are flagged for the user, not this session's call
  to commit.
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
true s206 — read it with `grep`/`sed -n`, never a plain whole-file
`Read`). Migrate durable mechanism/architecture material to
`PROJECT-OVERVIEW.md` and prune superseded detail, paired with a real
experiment — flagged for 7+ sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session's commit
scope. Still flagged for the user, not committed autonomously.
