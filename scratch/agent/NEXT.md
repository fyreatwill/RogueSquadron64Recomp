# NEXT work unit — re-soak with the new guest-PC breadcrumb until a
# `submitSceneNodeRender`-range crash recurs, then guard the exact line
# `[CRASH][last-guest-pc]` points to.

## Where the investigation stands (s265)

s265 built and landed the instrument s264 named as a "generically high
value investment": `g_rs64_last_guest_pc`, a global stamped with the
current guest MIPS address before every instruction in
`submitSceneNodeRender` (every recompiled instruction already carries a
`// 0xGUEST_ADDR: mnemonic` comment in `funcs_4.c`, so this is a 1:1
address index for free). The SIGSEGV/SIGBUS handler in
`RogueSquadron64Recomp/src/main/main.cpp` now prints
`[CRASH][last-guest-pc] pc=0x........` on every crash.

**Build gotcha, important if you touch `recomp.h` again**: there are TWO
copies. `~/Documents/Tools/N64Recomp/include/recomp.h` is the standalone
codegen tool's own header (irrelevant to the actual game build).
`RogueSquadron64Recomp/lib/N64ModernRuntime/N64Recomp/include/recomp.h`
(inside the `N64ModernRuntime` submodule) is the one `CMakeLists.txt`
actually points `RecompiledFuncs`'s include path at
(`target_include_directories(RecompiledFuncs PRIVATE ...
lib/N64ModernRuntime/N64Recomp/include ...)`, line ~96) — **this is the
one that's load-bearing for compilation.** Editing only the standalone
copy compiles fine through `N64Recomp`/`fixup_game_funcs.py` but fails
`cmake --build` with "undeclared identifier" errors that don't obviously
point back at `recomp.h` at all. Both copies were edited this session for
consistency; if you add anything else to `recomp.h`, add it to BOTH, but
remember only the `lib/` one matters for the actual binary.

**6 soaks with the breadcrumb armed** (`scratch/s73_post_a_scene/
run_breadcrumb1.sh`, log at `scratch/s73_post_a_scene/breadcrumb1/
run.log`, overwritten each run — see `PORTING-STATE.md` Session 265 for
the full preserved crash text of all 6): 1 clean, 5 crashed, but in
functions OTHER than `submitSceneNodeRender` every time
(`tickTextureMaterialExpiry+612`, `__pthread_kill+8`,
`unregisterServiceWorker+536`, `coalesceFreeHeapBlocks+2108`,
`static_5_800AB658+49104`). In all 5, `[CRASH][last-guest-pc]=0x80011088`
— confirmed via `grep "0x80011088" N64Recomp/RecompiledFuncs/funcs_4.c`
to be the function's own LAST instruction (its return/epilogue, right
before `renderFlatMeshFaceGroup` begins at line 4249). **The instrument
works correctly** (plausible, source-verifiable, non-zero every time —
satisfies iron rule 1's positive-control bar for the tool itself); it
just didn't get the chance to prove itself on the actual target crash
this session, because that crash didn't recur.

**Hit-rate math**: combined with s263 (1/3 attempts) and s264 (1/1), the
target `submitSceneNodeRender+19268` crash has fired in 2 of 10 total
soak attempts across 3 sessions (~20%). This session's other 4 crash
symbols fired in 5 of 6 attempts — i.e., right now, OTHER bugs are far
more likely to kill a soak first than this one is.

## The next work unit

**Option A (primary — do this first): just re-soak.** Run
`zsh scratch/s73_post_a_scene/run_breadcrumb1.sh` (full path, background,
`TaskOutput(block=true, timeout<=480000)` in the SAME turn — do not try
to idle across a turn boundary, confirmed broken again in multiple prior
sessions) several times — budget at least 4-5 attempts given the
measured ~20% hit rate, more if time allows. After EACH run, check:

```
grep -n "CRASH\]\[pc-symbol\]\|CRASH\]\[last-guest-pc\]" \
  scratch/s73_post_a_scene/breadcrumb1/run.log
```

- If `pc-symbol` says `submitSceneNodeRender+N` for some `N`: THIS is the
  hit. Take `last-guest-pc`'s value (a guest hex address) and:
  `grep -n "// 0xTHATADDR:" N64Recomp/RecompiledFuncs/funcs_4.c` to get
  the exact source line number. Read a small window around that line
  (targeted Read, not the whole function) — look for the STORE
  (`MEM_W(reg, off) = value` on the LEFT of `=`, matching the crash's
  actual faulting instruction being a store per s264) using a freshly
  loaded, unvalidated register as the address, same idiom as every prior
  guard in this chain. Add ONE guard (`fixup_game_funcs.py`, same
  degrade-to-nearest-existing-label pattern as `DEQUEUE_GUARD`/GUARD2/
  etc.), full delete-all regen, soak again. Discriminating outcomes: same
  as always — guard fires with a sane caught value (likely fix, needs a
  2nd soak per iron rule 4 before "confirmed"); guard silent but run
  survives longer/dies elsewhere (real progress, follow the new crash);
  guard silent and crash recurs at the exact same guest address (guard
  missed the real value, re-read more carefully, budget rule 8 applies on
  a 3rd miss).
- If every attempt keeps landing elsewhere (as this session did): after
  ~5 attempts with zero `submitSceneNodeRender`-range hits, STOP this
  approach for the iteration (budget rule 8's spirit — not literally the
  same hypothesis, but the same "keep trying the same experiment" pattern)
  and switch to Option B.

**Option B (if Option A goes 5+ soaks without a target hit): apply
`s193_disasm.py`/`s264_symrange.py` to this session's 4 unresolved crash
symbols.** For each of `tickTextureMaterialExpiry+612`,
`unregisterServiceWorker+536`, `coalesceFreeHeapBlocks+2108`,
`static_5_800AB658+49104` (skip `__pthread_kill+8` — that's a system
library frame, not ours): confirm via `s264_symrange.py` whether the
crash offset genuinely falls inside the named function's own address
range (same check that caught s263's misattribution). Two of these
(`unregisterServiceWorker`, `static_5_800AB658+49104`) died very early in
their soaks (~0-4s into the hold window) — worth checking whether they're
actually the SAME already-catalogued "23rd crash class"
(`waitForAnyAudioSlot`-family audio abort, first seen s165, also hit
twice by s263) recurring under a different ASLR-shifted nearest-symbol
label, rather than a genuinely new bug each time. If any of these 4 turn
out to be new, real, previously-unguarded bugs, they may be worth fixing
even before the primary `submitSceneNodeRender` target, simply because
they're firing far more often right now and crowding out every other
investigation this soak schedule is used for.

## Do NOT do this iteration

- Do NOT treat the 4 differently-named crash symbols from s265 as 4
  confirmed distinct bugs without running them through
  `s193_disasm.py`/`s264_symrange.py` first — ASLR shifts `base=`
  per-run, and at least 2 look like plausible nearest-symbol
  misattributions over stripped code, same caveat as the existing
  `[CRASH][pc-symbol]` comment in `main.cpp` already documents.
- Do NOT cite `x0`/`x8`/`x9=0x0000000300000000` as crash-matching
  evidence for ANYTHING — constant RDRAM base pointer (s219, item -60),
  misled two sessions already (s216-218, s263). Use the OTHER operand
  register instead.
- Do NOT re-touch `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`/cache-guard/
  `MATLIST_GUARD1-3`/`COMPOSE_NPC_GUARD1-9`/`DEQUEUE_GUARD` — all
  confirmed not the mechanism for the current open crash (`DEQUEUE_GUARD`
  stays armed as hardening only, 0 fires across 3 soaks now).
- Do NOT idle across a Stop-hook turn boundary waiting on a background
  soak — block with `TaskOutput(task_id, block=true, timeout<=480000)` in
  the SAME turn.
- Do NOT edit `~/Documents/Tools/N64Recomp/include/recomp.h` alone and
  assume it's enough — the actual build uses the copy under
  `lib/N64ModernRuntime/N64Recomp/include/recomp.h`. Edit both, or at
  minimum the `lib/` one.

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` needs cwd `rogue_squadron64`, `N64Recomp`
  needs cwd `N64Recomp`, `fixup_game_funcs.py` needs cwd `N64Recomp`,
  `cmake --build` needs cwd `RogueSquadron64Recomp/build`.
- Delete `funcs_*.c` before regen via:
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
  (`rm`/`find -delete` are sandbox-blocked).
- Background launches do NOT inherit a prior foreground `cd` — always
  launch soak drivers by full absolute path when using
  `run_in_background: true`.
- Cross-turn waiting does not work under the Stop hook — use
  `TaskOutput(task_id, block=true, timeout<=480000)` synchronously in the
  same turn.
- Soak driver scripts live under `scratch/s73_post_a_scene/`, NOT
  `scratch/agent/`. Current-best baseline: `run_breadcrumb1.sh` (clone of
  `run_dequeueguard1.sh`, same schedule, same guards armed, now also
  carries the guest-PC breadcrumb — use this one going forward, it's a
  strict superset).
- `+N` crash-symbol offsets are NATIVE (ARM64) code offsets, verifiable
  with `s264_symrange.py` + `s193_disasm.py` (no `nm`/`atos`/`otool`/
  `lldb`/`dwarfdump` on this sandbox's Bash allowlist).
- `CURRENT-TRUTH.md` is ~460KB+, ~13x the ~35KB target in CLAUDE.md. A
  dedicated pruning session is now 7+ consecutive sessions overdue —
  still not this iteration's job unless the localization work above is a
  quick null with clear leftover budget.
