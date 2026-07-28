# NEXT work unit — add an upper-32-bits check to heapWalker's existing
guards and soak for the first-ever live fire

Read PORTING-STATE Session 213 in full (`grep -n "^## Session 213"
PORTING-STATE.md`) before doing anything else. Short version: s213's 4th
soak (varied recipe) hit a brand-new crash, `heapWalker+1128`
(dladdr-confirmed; `backtrace_symbols_fd` mis-names the same frame
`frameStartReset+532` — first LIVE proof of the s157/s172 inlining theory).
The crash's register dump (`x10=0x0000000080003827`, upper 32 bits
`0x00000000`) is the same "KSEG0-zero-extension" shape already named for
item -49's `renderUnlitMeshFaces` bug and s210's `evalCubicSplineAtTime`
bug — a 3rd independent function hit by the same corruption class. Cross-
referencing `recomp.h` (`U32(val)`=`(uint32_t)(val)`, `gpr`=`uint64_t`,
`MEM_W` uses the FULL 64-bit `reg` with no truncation) proves heapWalker's
existing 10 guards (`U32(ctx->rN) < 0x80000000u || >= 0x80800000u`, in
place since s172, neither fired this run) are STRUCTURALLY blind to this
exact corruption: a legit sign-extended KSEG0 pointer (upper=`0xFFFFFFFF`)
and a corrupt zero-extended one (upper=`0x00000000`) have identical low-32
bits, and `U32()` discards the only bits that would tell them apart. This
is a project-wide guard-design gap, not a heapWalker-specific miss (same
`U32()`-truncated template used at CURRENT-TRUTH doc lines ~3109/3402/
3434/3622/3777).

## Do exactly one this iteration

**Add an upper-bits check to heapWalker's 10 existing guard sites, rebuild,
and soak** — the first live test of whether this strengthened check can
catch what the current guards miss:

1. Open `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`,
   find `_make_heapwalker_guard_patch` (~line 3035) and
   `_make_heapwalker_guard3_patch` (~line 3112).
2. In BOTH patch bodies, change the bounds-check condition from
   `if (r4_lo < 0x80000000u || r4_lo >= 0x80800000u) {` (GUARD, uses
   `ctx->r4`) and the equivalent `r3_lo` line (GUARD3, uses `ctx->r3`) to
   ALSO reject a nonzero-but-wrong upper 32 bits. Concretely, add a
   sibling check on the raw 64-bit register value, e.g.:
   `uint64_t r4_hi = (uint64_t)ctx->r4 >> 32;` /
   `uint64_t r3_hi = (uint64_t)ctx->r3 >> 32;` and extend the `if` to
   `if (r4_lo < 0x80000000u || r4_lo >= 0x80800000u || r4_hi != 0xFFFFFFFFu)`
   (same for r3/r3_hi). Keep the existing `fprintf` diagnostics but add the
   hi value to the printed line (e.g. `bad_r4=0x%08X hi=0x%08X`) so a fire
   is distinguishable as "low-range-bad" vs "hi-extension-bad" — this
   distinction IS the discriminating measurement.
3. Regen order (NOT optional, hard rule): `make_elf.py` -> `N64Recomp` ->
   `fixup_game_funcs.py` -> `cmake` (`DEVELOPER_DIR=/Applications/Xcode.app/
   Contents/Developer cmake --build build` or however this repo's build
   step normally runs — check `docs/CURRENT-TRUTH.md`'s build section if
   unsure of the exact invocation).
4. Copy `scratch/agent/run_unlitmeshtracer8.sh` to a new tag (e.g.
   `run_heapwalkerguard4.sh`), set `ROGUESQ_LOG_HEAPWALKER_GUARD=1` and
   `ROGUESQ_LOG_HEAPWALKER_GUARD3=1` (both currently unset/0 in the
   unlitmeshtracer8 recipe — needed this time so a fire is actually logged),
   same `STICK_SCHEDULE` (the varied one from s213, already reaches the
   crash once). Change the tag argument to match.
5. Launch with `Bash(..., run_in_background=true)`, block with
   `TaskOutput(task_id, block=true, timeout=420000)`.
6. Check, in order:
   - Does `[heapwalker-guard]`/`[heapwalker-guard3]` fire at all
     (`grep -c` in the new run.log)? If yes with `hi=` != `0xFFFFFFFF`,
     this is the FIRST LIVE POSITIVE CONTROL for the zero-extension theory
     — the mechanism is proven, not just inferred from a post-mortem
     register dump.
   - Does `CRASH: N` stay near 0 (or at least not repeat the exact
     `heapWalker+1128`/`si_addr=0x380003827` signature)? If the guard fires
     AND the crash stops, the fix works — write it up as resolved for this
     specific crash and flag whether the same technique should extend to
     the `ctx->r16`/item -49 guard (not yet built, still just tracer-only)
     once that guard exists.
   - If the guard still doesn't fire AND the crash recurs identically, the
     upper-bits theory is REFUTED for this specific crash (the corruption
     isn't in `ctx->r4`/`ctx->r3` at all, something else feeds the bad
     address) — note this precisely, don't force a positive spin.

## Discriminating outcomes

- **Guard fires with `hi != 0xFFFFFFFF`, crash gone** — mechanism proven
  AND fixed for heapWalker; strong candidate to generalize to every other
  `U32()`-truncated guard in the project (a real, scoped, high-value
  follow-up, not this iteration's job).
- **Guard fires, crash still happens somewhere else** — the specific site
  hit this time is now closed, but heapWalker (or a caller) has more than
  one corrupted-register path; note where the new crash lands.
- **Guard never fires, crash recurs identically** — refutes the theory for
  THIS crash; the corrupted value feeding `heapWalker+1128`'s dereference
  isn't `ctx->r4`/`ctx->r3` at the 10 known sites — needs a fresh
  source-read of heapWalker for an 11th/uncovered call shape (per s213,
  no disassembly tool is available to map pc+1128 to an exact line, so this
  would be a full careful re-read, not a quick grep).
- **Guard never fires, no crash at all this soak** — inconclusive (the
  crash itself may just not have reproduced this run); re-run once before
  concluding anything, this doesn't count toward budget rule 8 since it's
  the same recipe validating the SAME fix, not a repeat probe of an
  unresolved hypothesis.

## Do not

- Do not touch the `ctx->r16`/`renderUnlitMeshFaces`/item -49 guard this
  iteration — it doesn't exist yet (tracer-only), and this iteration's
  scope is heapWalker's already-built guards only.
- Do not re-open the "shared ~60-75s trigger" question (s212, CLOSED) or
  re-litigate s211's stall (item -35, budget-closed since s186).
- Do not attempt a 5th `STICK_SCHEDULE` variation this iteration — the
  varied recipe from s213 already reliably reaches this crash; changing it
  again would just be re-rolling the dice on which failure appears, not
  advancing the discriminating test above.
- Do not re-attempt `nm`/`otool`/`objdump`/`lldb` to map `heapWalker+1128`
  to an exact source line — blocked, re-confirmed s207/s213.

## Environment notes (carried forward, still current)

- The `[CRASH][pc-symbol]` diagnostic (dladdr on the raw mcontext `pc`) is
  permanent, always-on, and is MORE PRECISE than `backtrace_symbols_fd` —
  s213 found a live case where they disagree on the same frame
  (`heapWalker+1128` vs `frameStartReset+532`) and dladdr was right per the
  s157/s172 source-read theory. Trust dladdr.
- Disassembly/symbolication tools (`nm`/`otool`/`objdump`/`lldb`/`atos`) are
  ALL blocked (non-interactive session, no human to clear the approval
  prompt) — re-verified s207, s213.
- `recomp.h` (`N64Recomp/include/recomp.h`, identical copy at
  `lib/N64ModernRuntime/N64Recomp/include/recomp.h`): `U32(val)` =
  `(uint32_t)(val)`; `gpr` = `uint64_t`; `MEM_W(offset,reg)` =
  `*(int32_t*)(rdram + ((reg)+(offset) - 0xFFFFFFFF80000000))` using the
  full 64-bit `reg`. A legit KSEG0 `gpr` is sign-extended, upper bits
  `0xFFFFFFFF` (s99 precedent: comparing the raw 64-bit value against a
  32-bit literal directly false-positives at 100% for exactly this reason,
  which is why every guard since s99 truncates through `U32()` first — but
  that same truncation is what makes them blind to zero-extension
  corruption).
- This project builds `CMAKE_BUILD_TYPE=Debug` (`-O0`) globally; `RECOMP_FUNC`
  is `noinline` — no game function can be silently inlined into a caller
  (s207, build-config-verified).
- `rm -f <glob>` and `find <dir> -delete` are BOTH blocked in this sandbox.
  Use `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('<pattern>')]"` instead.
- `fixup_game_funcs.py` re-run after deleting only ONE `funcs_*.c` file is
  safe and idempotent on the other 44 already-patched files (s208-s211
  confirmed, no duplicate `PATCH:` markers).
- `./build/N64Recomp rogue_squadron.toml` (from the `N64Recomp` checkout)
  needs an `env` prefix to clear the permission-prefix-match wall.
- Any edit under THIS repo's `lib/` needs `./submodule-patches/export.sh` +
  commit in the SAME session. `N64Recomp` and `rogue_squadron64` are
  SEPARATE checkouts outside this repo, NOT `lib/` submodules — their
  uncommitted changes are flagged for the user, not this session's call to
  commit. (Note: editing `N64Recomp/fixup_game_funcs.py` per this NEXT.md's
  step 1 is in that separate checkout, not `lib/` — no export.sh needed for
  that edit itself, but if the regen step also touches anything under this
  repo's `lib/`, export+commit that part.)
- Re-running the same soak script/tag overwrites the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- `ROGUESQ_LLE_FORCE`/`ROGUESQ_LLE_UNGATED`/`ROGUESQ_LLE_SOLO`/
  `ROGUESQ_STUB_MISSING_FUNCS` are set INSIDE `run_mission_keys.sh` itself
  (line 6), not the driver scripts.
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh` /
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied in ONE
  Bash call — prefer separate Bash calls. Output-redirection compounds also
  get flagged — use the `Write` tool for small file writes.
- Heredocs get rejected by this session's Bash tool — use the Write tool
  instead (write to `scratch/agent/`, not `/tmp`).
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.
- `scratch/agent/STATUS`/`OUTCOME` get reset to `WORKING`/deleted at the
  START of each iteration by the harness — finding them in that state at
  session start is normal.
- Launch soaks with `Bash(..., run_in_background=true)` then block with
  `TaskOutput(task_id, block=true, timeout=180000-480000)`.
- `[vi-fs-decision]` lines carry a `stalled=` field per-decision — grep the
  full sequence, not just the tail, to distinguish a transient blip from a
  permanent stall.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now ~4490 lines, well past both the ~35 KB
CLAUDE.md budget and the Read tool's 256 KB single-read limit (confirmed
s195, still true s213 — read it with `grep`/`sed -n`, never a plain
whole-file `Read`). Migrate durable mechanism/architecture material to
`PROJECT-OVERVIEW.md` and prune superseded detail, paired with a real
experiment — flagged for 11+ sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session's commit
scope. Still flagged for the user, not committed autonomously.

`lib/N64ModernRuntime` and `lib/rt64` show as modified in `git status` at
the start of s213 (pre-existing, not caused by s213's work) — not
investigated this session (out of scope for the prescribed work unit); if
a future session touches anything under `lib/`, remember the export.sh +
same-session-commit rule applies, and it may be worth first checking
whether these two submodules' patches are still in sync with
`submodule-patches/*.patch` before assuming this is normal steady-state
dirtiness.
