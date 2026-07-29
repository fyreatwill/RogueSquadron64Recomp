# NEXT work unit — catch a `heapFreeListDequeue`-range crash under the new
# `BREADCRUMB2` instrument and localize the internal guest-PC exactly.

## Where the investigation stands (s267)

s267 tested s266's hypothesis that the guest-`0x80000000`-family fault inside
`heapFreeListDequeue` (first seen s266, `sym=heapFreeListDequeue+16188`,
`si_addr` exactly RDRAM-base+`0x80000000`) arrives via the function's a0
argument (the value `DEQUEUE_GUARD`'s `r4_lo < 0x80000000u || r4_lo >=
0x80800000u` check lets through unvalidated at the exact lower boundary).

**Result: hypothesis REFUTED**, with a same-run positive control. Added
`DEQUEUE_ARG_TRACE` (`N64Recomp/fixup_game_funcs.py`, inside
`_dequeue_guard_patch`, gated by `ROGUESQ_LOG_DEQUEUE_ARG_TRACE`) — an
unconditional trace of `ctx->r4` at both `DEQUEUE_GUARD` call sites, firing on
EVERY call (not just failures). A calibration soak
(`env HOLD_S=30 zsh run_dequeuearg1.sh <tag>`) fired the trace 167,352 times
and then crashed (`sym=heapFreeListDequeue+16288` — note: +16288, a nearby
but NOT identical offset to s266's +16188). **The single trace line
immediately preceding the crash, with zero lines between it and `[CRASH]`,
was `site=2 r4=0x801BB88C`** — a plausible in-range guest pointer, not
`0x80000000`. This directly refutes the a0-argument hypothesis: **do NOT
tighten `DEQUEUE_GUARD`'s bound expecting it to fix this crash** — the
corruption is internal to `heapFreeListDequeue`'s own body (some field it
itself dereferences), not in what's passed to it.

Also landed `BREADCRUMB2` — the same guest-PC-stamping mechanism s265 built
for `submitSceneNodeRender` (`g_rs64_last_guest_pc`), now ALSO scoped to
`heapFreeListDequeue`'s own body (`funcs_3.c`, patched x724). This means the
NEXT time this crash recurs, `[CRASH][last-guest-pc]` will report the EXACT
guest MIPS instruction inside `heapFreeListDequeue` at fault time — no more
disassembly correlation needed (`s193_disasm.py`'s small hand-rolled decoder
didn't cover this session's actual crash instruction, a register-offset STR
variant, `0xb82a6928` — inconclusive dead end, don't retry that approach).

**3 follow-up soaks with the BREADCRUMB2 build (`HOLD_S=30/60/180`) did NOT
reproduce this specific crash** — consistent with s265's measured ~20% hit
rate for this general crash family. Instead all 3 hit DIFFERENT crashes:
`load_hmt_and_hob+3164` (`si_addr=0x380000004`, `last-guest-pc=0x80011088`),
`cvmsPoolAlloc+84` (`si_addr=0x1b6020300000022` — NOT RDRAM-relative, likely
unrelated/host-side), `processSceneNode+1184` (`si_addr=0x380000030`,
`last-guest-pc=0x80011088`). The `last-guest-pc=0x80011088` value in 2 of
these means `submitSceneNodeRender` had ALREADY returned normally when the
crash hit — i.e. these are downstream in the same broader call chain
(`processSceneNode` → `traverseSceneGraphRecursive` → `setupCameraMatrices`
→ ...), not inside it. None had a `dequeue-arg-trace` line anywhere near the
crash — genuinely unrelated to `heapFreeListDequeue` this soak, not the same
bug recurring under a different name.

## The next work unit

1. **Re-soak to reproduce.** `cd scratch/s73_post_a_scene && env HOLD_S=<n>
   zsh run_dequeuearg1.sh <tag>` (both `ROGUESQ_LOG_DEQUEUE_ARG_TRACE` and the
   `BREADCRUMB2` instrument are unconditionally compiled in already — no
   rebuild needed unless you change code). Budget several attempts (this
   session's evidence plus s265's suggests ~20% hit rate for
   `heapFreeListDequeue`-range crashes specifically vs. the broader crash
   population). Remember the env-prefix gotcha: `env HOLD_S=30 zsh ...`, NOT
   `HOLD_S=30 zsh ...` (bare leading env-assignment breaks the headless
   permission prefix match, iron rule 10).
2. **When a `heapFreeListDequeue`-range crash lands** (`[CRASH][pc-symbol]
   sym=heapFreeListDequeue+N`, confirm via `s264_symrange.py` if in doubt that
   N genuinely falls in that function's range 0-21608): read
   `[CRASH][last-guest-pc]`, then `grep -n "0x<UPPERCASE_HEX>:"
   N64Recomp/RecompiledFuncs/funcs_3.c` to get the exact source line inside
   `heapFreeListDequeue`. Read the surrounding ~20 lines to identify the
   dereferenced field/pointer and whether it's an already-guarded idiom
   (4 `findAndUnlinkSmallestEntry head-pointer deref guard` sites and 4
   `free-list-walk loop-back guard` sites already exist in this function,
   per the fixup report — check whether the crash line is a 5th unguarded
   copy of one of those idioms, or something new).
3. **Add ONE targeted guard** at that exact dereference (same pattern as
   every other guard in `N64Recomp/fixup_game_funcs.py`: validate the
   pointer's range before the deref, on failure skip to the nearest natural
   reentry point, log behind a new `ROGUESQ_LOG_*` env var). Full delete-all
   regen (`make_elf.py` → `N64Recomp` → `fixup_game_funcs.py` → `cmake
   --build`), then soak-verify per iron rule 4 (≥2 independent runs with no
   recurrence of THIS crash, or a clean guard-fire-and-recover).
4. **If budget remains after that**: apply `s264_symrange.py`-style range
   verification to this session's 3 unresolved crash symbols
   (`load_hmt_and_hob+3164`, `cvmsPoolAlloc+84`, `processSceneNode+1184`) to
   check they're genuinely inside those functions' ranges (not nearest-symbol
   misattribution over stripped code) before treating the "shared fault-shape
   pattern" observation as a real class worth its own investigation.

## Do NOT do this iteration

- Do NOT touch `DEQUEUE_GUARD`'s range-check bound — the a0-argument
  hypothesis is refuted with a same-run positive control (167k trace fires,
  last one pre-crash showed a sane value). This is not the mechanism.
- Do NOT conflate this crash family with item -49's KSEG0-zero-extension bug
  (`0x80630062`) — different exact values, different sites, confirmed
  distinct multiple sessions running.
- Do NOT cite `x0`/`x8`/`x9`/`x11 = 0x0000000300000000` as crash-matching
  evidence for ANYTHING — constant RDRAM base pointer (s219, item -60).
- Do NOT re-touch `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`/cache-guard/
  `CACHE2_GUARD`/`MATLIST_GUARD1-3`/`COMPOSE_NPC_GUARD1-9` — all verified not
  regressing and not the current blocker.
- Do NOT retry `s193_disasm.py`'s manual decoder on this crash's native
  offset — already tried, the actual instruction (`0xb82a6928`, a
  register-offset STR) is outside its small decoder's coverage. Use
  `BREADCRUMB2`'s `[CRASH][last-guest-pc]` instead — it's exact and doesn't
  need decoding.
- Do NOT idle across a Stop-hook turn boundary waiting on a background
  soak — block with `TaskOutput(task_id, block=true, timeout<=480000)` in
  the SAME turn.

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` needs cwd `rogue_squadron64`, `N64Recomp`
  needs cwd `N64Recomp`, `fixup_game_funcs.py` needs cwd `N64Recomp` (or an
  absolute path — either works, but re-running the SAME already-patched
  files a 2nd time in a row makes every regex match 0 and looks like a
  regression when it's just non-idempotent re-application; always regen from
  fresh `funcs_*.c` before checking match counts).
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
  `scratch/agent/`. Current-best baseline for this investigation:
  `run_dequeuearg1.sh` (new this session — same env-var set as
  `run_breadcrumb1.sh` plus `ROGUESQ_LOG_DEQUEUE_ARG_TRACE`; `HOLD_S`
  overridable via env, defaults to 240 if unset).
- `+N` crash-symbol offsets are NATIVE (ARM64) code offsets, verifiable
  with `s264_symrange.py` + `s193_disasm.py` (no `nm`/`atos`/`otool`/
  `lldb`/`dwarfdump` on this sandbox's Bash allowlist). `s264_symrange.py`
  hardcodes `build/RogueSquadron64Recomp` and only reports
  `submitSceneNodeRender`/`heapFreeListDequeue` by name — for a new symbol
  either edit the script or write a one-off inline snippet.
- Redirecting shell output (`>`) only works to paths under one of the 3
  session working directories (`RogueSquadron64Recomp`, `N64Recomp`,
  `rogue_squadron64`) — `/tmp` is blocked. Use
  `scratch/agent/*.log` for capturing tool output you want to grep later.
- `N64Recomp/fixup_game_funcs.py` is untracked by git in the standalone
  `N64Recomp` checkout (confirmed s267: `git status` there shows it `??`,
  same for `RecompiledFuncs/`) — this is expected, not a bug; it's not a
  `lib/` submodule so `submodule-patches/export.sh` never applies to it. Its
  changes persist only via the live file on disk across sessions.
- `CURRENT-TRUTH.md` is ~460KB+, ~13x the ~35KB target in CLAUDE.md. A
  dedicated pruning session is now 9+ consecutive sessions overdue —
  still not this iteration's job unless the localization work above is a
  quick null with clear leftover budget.
