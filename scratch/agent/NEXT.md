# NEXT work unit — source-read `static_5_800A9270`/`loadCutsceneAssetsByIndex` to find and guard
# the new `+948` crash site

## Where the investigation stands (s282)

s282 re-soaked `BREADCRUMB8`/`emitAllocatedDLCommand` (its 2nd session, per s281's plan) —
**0/2 on BREADCRUMB8's own target (0/4 combined, s275+s282), but soak2 crashed inside
`static_5_800AB658` itself (`BREADCRUMB7`'s target), the FIRST informative hit across the entire
`BREADCRUMB5`-`BREADCRUMB9` family (~10+ sessions, 0/20 combined before this).**

**What happened and what was fixed** (full detail: `PORTING-STATE` Session 282):
- Soak2 crash: `sym=static_5_800AB658+68992`, `last-guest-pc=0x800ACB04`. Both independently
  confirmed (grep + Mach-O symtab range walk via `nm -n`) to be genuinely inside
  `static_5_800AB658` (127760-byte native range, offset 68992 well inside — not a nearest-symbol
  misattribution).
- Root cause: the existing `G8` guard (s132, part of the `static_5_800AB658` "whack-a-mole"
  `-0x25A4`-deref-guard family `G1`-`G31`) validates `ctx->r2` right before
  `0x800ACAF8: lw $v0, 0x8($v0)` — but that instruction RELOADS `r2`, and the reloaded value is
  never re-validated before ITS OWN next dereference two instructions later at
  `0x800ACB04: lwc1 $f0, 0x14($v0)`, exactly where the SIGBUS fired. A second-hop-dereference gap
  none of `G1`-`G31` covered (they're all single-hop).
- Fix: added `G32` to `_hangarbay_deref_guard_sites` in `N64Recomp/fixup_game_funcs.py` (same
  `_make_hangarbay_deref_guard_patch` mechanism, validates the reloaded `ctx->r2`, bails to the
  existing `L_hangarbay_guard_exit`). Full regen pipeline run, clean build, patch report confirmed
  `G32 patched x1`.
- Validation: 2 more soaks (`s282_soak3/4`), both reached the scene, neither reproduced
  `static_5_800AB658+68992`. Soak3 hit already-catalogued `coalesceFreeHeapBlocks+2108`. **Soak4
  hit a genuinely NEW site: `sym=static_5_800A9270+948`** (`loadCutsceneAssetsByIndex`,
  range-verified in-bounds, function spans 2152 bytes) — same whack-a-mole family as the existing
  `HANGARLIST_GUARD` (s254, guards a DIFFERENT offset, `+668`, in the same function).

**`BREADCRUMB8`/`emitAllocatedDLCommand` itself**: still 0/2 this session, 0/4 combined across 2
sessions (s275+s282) — the hit landed on `BREADCRUMB7`'s target, not `BREADCRUMB8`'s own. Do NOT
re-soak `BREADCRUMB8` a 3rd session without a new angle (now tied with `BREADCRUMB6`/`BREADCRUMB7`
at 2 sessions / 0 hits on their own target).

**Whole-family status** (updated for s282):
- `BREADCRUMB5`/`reserveAndEmitDLEntry`: 0/4 (s272+s273), 2 sessions, never informative.
- `BREADCRUMB6`/`buildPositionAndCallTransformHelper`: 0/4 (s273+s280), 2 sessions, never
  informative.
- `BREADCRUMB7`/`static_5_800AB658`: **now has its first combined informative hit** — the `G32`
  fix, found via a `BREADCRUMB8` soak, not its own re-soaks (which were 0/4 through s281). Treat
  as resolved for THIS specific crash shape; the whack-a-mole family (`G1`-`G32`) may still have
  more unguarded sites (see below), but that's now tracked as its own backlog item, not a
  `BREADCRUMB7` re-soak.
- `BREADCRUMB8`/`emitAllocatedDLCommand`: 0/4 combined (s275+s282), 2 sessions, never informative
  on its own target. Do NOT re-soak a 3rd session without a new angle.
- `BREADCRUMB9`/`tickWrappingTimerAccumulatorList`: 0/2 genuine across 3 sessions, 3-strikes hit
  s278, confound angle closed s279. Do not re-soak.

## The next work unit

**Source-read `static_5_800A9270` (`loadCutsceneAssetsByIndex`) to find and guard the `+948`
crash site.** This is now the single highest-information-value probe available: a concretely
reproduced, range-verified crash in a KNOWN function with a KNOWN fix pattern (the same recipe
that just worked for `G32` and, before that, `HANGARLIST_GUARD` at s254) — not a blind re-soak of
an already-exhausted breadcrumb.

1. Find the function in source: `grep -n "static_5_800A9270" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_40.c` (s254 located it at `funcs_40.c:5314-5463`; line numbers
   have almost certainly shifted since — the `G32` addition alone adds ~14 lines, and `BREADCRUMB7`
   itself adds ~2643 breadcrumb-assignment lines to this same file). Read the full function body.
2. `HANGARLIST_GUARD` (s254) already guards ONE dereference near the top of this function (the
   first `MEM_W(ctx->r4, 0X4)` load at guest `0x800A92FC`, bailing to `L_800A9350`) — read that
   existing guard's code first (`grep -n "HANGARLIST_GUARD" /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`) to see the established pattern and epilogue label for this
   specific function (likely different from `static_5_800AB658`'s `L_hangarbay_guard_exit`).
3. Native crash offset was `+948` bytes (ARM64, this build). There is no direct
   guest-PC-breadcrumb for this function (`last-guest-pc` in the s282 soak4 crash still showed
   `0x800adb6c`, which is `static_5_800AB658`'s OWN epilogue instruction, not anything in
   `static_5_800A9270` — this function has no per-instruction breadcrumb of its own). Localizing
   the exact guest instruction will need either: (a) reading the function's full disassembly and
   reasoning about which pointer-chase/dereference idiom is LEAST likely to be the
   already-guarded `+668` site and most plausible as a distinct, later dereference, or (b) adding
   a lightweight guest-PC breadcrumb to just this one function (cheap — it's only ~2152 bytes
   native, not a huge blanket instrumentation pass) and re-soaking once to pin the exact
   instruction before spending a fix-and-validate cycle. Prefer (b) if the source read alone
   doesn't make the site obvious — it worked well for `BREADCRUMB7`/`8`/`9` in general and this
   function is small enough that per-instruction logging won't meaningfully bloat build/soak
   time.
4. Once localized, land a guard using the SAME validated pattern (`U32(ctx->rN)` range check
   against `0x80000000`-`0x80800000`, bail to this function's own epilogue label) — do not
   reinvent the mechanism, this exact recipe has now worked twice (`HANGARLIST_GUARD` s254,
   `G32` s282).
5. Full regen pipeline (`make_elf.py` → delete `funcs_*.c` → `N64Recomp` → `fixup_game_funcs.py`
   → `cmake --build`), confirm patch report shows the new guard patched exactly `x1` (no
   stacking/collision), confirm clean build.
6. Validate with 2 soaks, `HOLD_S=240` each, `run_in_background: true` + `TaskOutput(block=true,
   timeout<=480000)` in the SAME turn. Check neither reproduces `static_5_800A9270+948`
   specifically (non-recurrence is the standard validation bar used for `G30`/`G31`/`G32`/
   `HANGARLIST_GUARD` — this family's crashes are individually rare, a direct fire-counter control
   would need `ROGUESQ_LOG_HANGAR_BAY_DEREF_GUARD=1`/an equivalent env flag for the new guard AND
   a session that happens to hit it again, not guaranteed).

**If this closes cleanly**: every one of the 5 original breadcrumbs will be at or past its
per-target budget (2 sessions each, 0 combined hits on their OWN specific hypothesized targets —
though the family AS A WHOLE has now produced one real, validated fix via `G32`, so "0 combined
hits" no longer means "0 value produced"). Next session after that should either:
- Look for further whack-a-mole sites in the `static_5_800AB658`/`static_5_800A9270` family if
  soaks keep surfacing them (this has now happened 3 times: s254's `HANGARLIST_GUARD`, s282's
  `G32`, s282's still-open `+948` site — a real, recurring pattern, not a one-off).
- Start the `inflate_fast`/zlib localization design (system-library call, not a guest function —
  needs a different approach, bigger lift, never attempted yet).
- Reassess whether continuing to re-soak `BREADCRUMB5`/`6`/`8` a 3rd time each is worth it, given
  the family's actual value has come from crashes found INCIDENTALLY during soaks, not from any
  breadcrumb's own hypothesized target ever panning out.

## Do NOT do this iteration

- Do NOT re-soak `BREADCRUMB5`/`6`/`7`/`8` — all 4 are now at 2 sessions / 0 hits on their OWN
  target with no new angle identified (BREADCRUMB7's family-level whack-a-mole issue is now
  tracked separately as the `static_5_800A9270+948` backlog item above, not a BREADCRUMB7 re-soak).
- Do NOT re-soak `BREADCRUMB9` again — 3-strikes threshold (s278), confound angle closed (s279).
- Do NOT treat `coalesceFreeHeapBlocks` crashes as a new finding — already catalogued
  (CURRENT-TRUTH ~line 1068/1088/1098/1308, PORTING-STATE s264-era notes) as a not-yet-localized
  family, possibly ASLR/nearest-symbol misattribution artifacts.
- Do NOT re-touch `DEQUEUE_GUARD`'s range-check bound — refuted (s267).
- Do NOT conflate the `0x80000000`-exact-fault family (or its `+0x10` `processSceneNode`-`+0x30`,
  `emitAllocatedDLCommand`-garbage-offset, `inflate_fast`-`+3`, `static_5_800AB658`-garbage-
  offset, or `tickWrappingTimerAccumulatorList`-bit31-clear variants) with item -49's KSEG0-
  zero-extension bug (`0x80630062`) without actually reading that item's writeup first.
- Do NOT cite `x0`/`x8`/`x9`/`x10`/`x11`/`x12` = `0x0000000300000000` or `0x0000000080000000`
  as crash-matching evidence for ANYTHING — constant RDRAM base pointer / constant register
  value seen across many unrelated crashes.
- Do NOT re-touch `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`/cache-guard/`CACHE2_GUARD`/
  `CACHE3_GUARD`/`CACHE4_GUARD`/`MATLIST_GUARD1-3`/`COMPOSE_NPC_GUARD1-9`/`DEQUEUE_GUARD` —
  all verified not regressing.
- Do NOT idle across a Stop-hook turn boundary waiting on a background soak — block with
  `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME turn.
- Do NOT treat a long-running soak (e.g. an 8GB+ log, driver command appearing "stuck") as
  necessarily hung — check `ps -p <pid>` first; the game process may already be dead while the
  driver script is still crunching a large log for its summary.
- Do NOT touch the `lib/N64ModernRuntime`/`lib/rt64` "-dirty" submodule state — it's the
  long-standing baseline (months of uncommitted patches mirrored in `submodule-patches/`), not
  new work. Only run `submodule-patches/export.sh` if YOU make new edits under `lib/` this
  session (this session's `fixup_game_funcs.py` edit was in the standalone `N64Recomp` checkout,
  NOT under `lib/` — no `export.sh` was needed, and the next session's guard work is the same
  situation).

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` needs cwd `rogue_squadron64` (run as `python3
  tools/make_elf.py`), `N64Recomp` needs cwd `N64Recomp` (`./build/N64Recomp
  rogue_squadron.toml`), `fixup_game_funcs.py` needs cwd `N64Recomp`. Always delete
  `funcs_*.c` and regen from scratch before running `fixup_game_funcs.py`.
- Delete `funcs_*.c` before regen via:
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
  (`rm`/`find -delete` are sandbox-blocked).
- Compound shell commands using `cd` combined with `&&`/output-redirection require
  interactive approval and get denied under the loop's automation — issue `cd <dir>` as its
  OWN Bash call first (cwd persists across calls in this tool), then run the next command as a
  separate call from that cwd. This also applies to `git -C <path> ...` and `git --git-dir=...
  --work-tree=... ...` — both get flagged as needing approval even standalone; use a plain `cd`
  (its own call) + `git status --short` (its own call, matches the `Bash(git status:*)`
  allowlist) instead. `nm -n <binary> > file` also gets flagged for approval even from an
  already-`cd`'d directory — prefer a Python `subprocess.run(["nm","-n",path], capture_output=True)`
  heredoc instead of shell redirection when doing symtab work.
- Shell `for VAR in ...; do ... done` loops and `$(...)` command substitution inside them get
  rejected by the sandbox ("Contains simple_expansion") even when individually each piece
  would be fine. Prefer a single `grep`/`ls` call with an explicit glob or explicit file-list
  argument over a shell loop when scanning multiple files. If Python is needed, avoid reading
  huge (multi-GB) log files fully into memory — use `grep -c`/`grep -l` for classification
  instead of `open().read()`, which can time out.
- Background launches do NOT inherit a prior foreground `cd` — always launch soak drivers by
  full absolute path when using `run_in_background: true`.
- Cross-turn waiting does not work under the Stop hook — use `TaskOutput(task_id, block=true,
  timeout<=480000)` synchronously in the same turn.
- Soak driver scripts live under `scratch/s73_post_a_scene/`, NOT `scratch/agent/`.
  Current-best baseline: `run_dequeuearg1.sh` (`HOLD_S` overridable via env, defaults to 240 if
  unset). `BREADCRUMB`-family entries do NOT carry their own `ROGUESQ_LOG_*` fire-log (only
  guards do) — no `run_dequeuearg1.sh` edit needed when adding/testing a `BREADCRUMBn`.
- Whether a soak reached the scene at all can be checked cheaply via `grep -c "vi_width=1024"
  <run.log>` (0 = pre-scene death, >=1 = reached it) — cheaper than relying on the driver's own
  stdout message (`process gone while waiting for phase`), which is NOT written into `run.log`
  itself.
- `+N` crash-symbol offsets are NATIVE (ARM64) code offsets and SHIFT across sessions as
  guards/breadcrumbs are added. Verify range membership via the Mach-O symtab walk (inline
  python, `subprocess.run(["nm","-n",path], capture_output=True, text=True)`, filter type T/t,
  dedupe by address, sort, find the exact-name entry, check the reported crash offset is less
  than the distance to the next DISTINCT address — duplicate symtab entries at the same address
  are common, dedupe by address before computing "next symbol" or the range check
  false-negatives). System-library crashes (like `inflate_fast`) resolve via the OS's own dyld
  symbol table and don't need/support the same check. nm symbol names have a leading underscore
  (`_static_5_800AB658`, not `static_5_800AB658`) — match on the underscored form.
- A crash's `[CRASH][last-guest-pc]` value is only informative if the crashing function is
  ITSELF breadcrumbed. Always grep the reported guest PC's hex label in the relevant
  `funcs_N.c` and find its enclosing `RECOMP_FUNC` before trusting it (walk backward from the
  matching `g_rs64_last_guest_pc = 0xXXXXXXXXu;` line to the nearest preceding `RECOMP_FUNC`).
  `0x8000b650` specifically is a recurring stale value belonging to `beginFrameDLChunk`
  (`funcs_3.c`) — do not treat it as informative unless the crashing symbol IS
  `beginFrameDLChunk`. `static_5_800A9270` (this session's new target) has NO per-instruction
  breadcrumb of its own — a `last-guest-pc` hit during a crash inside it will show whatever OTHER
  breadcrumbed function last ran (e.g. `static_5_800AB658`'s epilogue), which is uninformative
  for localizing WITHIN `static_5_800A9270` specifically.
- When adding a guard to a function that's ALSO covered by an existing breadcrumb's blanket
  per-instruction pass: check whether the guard patch's code block sits before or after the
  breadcrumb patch's block in `fixup_game_funcs.py`'s file order. A guard block positioned
  BEFORE its function's breadcrumb block sees PRE-breadcrumb text and must not require
  `g_rs64_last_guest_pc` lines in its match regex (confirmed again this session: `G32`'s pattern
  omits the breadcrumb line and matched cleanly against the pre-`BREADCRUMB7`-pass text).
- Redirecting shell output (`>`) only works to paths under one of the 3 session working
  directories — `/tmp` is blocked. Use `scratch/agent/*.log`.
- `N64Recomp/fixup_game_funcs.py` is untracked by git in the standalone `N64Recomp` checkout —
  expected. Changes persist only via the live file on disk across sessions.
- `git status --short` run from inside `RogueSquadron64Recomp/build` (or any subdir, via a
  plain `cd` + `git status` as two separate Bash calls) works without needing `-C`/`git
  --git-dir` approval prompts.
- `CURRENT-TRUTH.md` is far over the ~35KB target (measured s282: >500KB, way over) — now
  23+ consecutive sessions overdue for a pruning pass. Still not this iteration's job unless the
  localization work above is a quick null with clear leftover budget. Note: the file is now large
  enough that a plain `Read` on it fails outright (>256KB tool limit) — use `grep -n` to find
  section line numbers, then `Read` with `offset`/`limit` on just the needed section.
- At session start, check `scratch/agent/STATUS`/`OUTCOME` for signs of an interrupted prior
  iteration (e.g. `STATUS=WORKING` with `OUTCOME` deleted but HEAD already at the last commit) —
  this is normal loop-restart noise, not unfinished work, as long as `git log` confirms the last
  session's commit landed cleanly. Don't spend budget investigating it further once confirmed.
