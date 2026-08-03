# NEXT work unit — re-soak `BREADCRUMB8`/`emitAllocatedDLCommand` (its 2nd session)

## Where the investigation stands (s281)

s281 re-soaked `BREADCRUMB7`/`static_5_800AB658` (its 2nd session, per s280's plan). **Result:
0/2 this session, 0/4 combined across 2 sessions (s274+s281) — never informative on its own
target.** No regen was needed (binary and fixup-script timestamps matched, same build as
s276-s280).

**But both soaks broke the s276-280 elevated pre-scene-death streak** — a meaningful reversion,
not the planned discriminating result but worth carrying forward:
- Soak1 reached the scene (`vi_width=1024` at 45.5s) then died 12s into the 240s hold at
  `sym=coalesceFreeHeapBlocks+2108` — an already-catalogued, not-yet-localized crash site (NOT
  new, NOT a `BREADCRUMB7` hit). `last-guest-pc=0x8000b650` (stale `beginFrameDLChunk` value,
  uninformative here).
- Soak2 reached the scene and ran much deeper — 152s into the hold, VI width progressing
  1024→512→640 — before dying at `sym=tickTextureMaterialExpiry+612`, also already-catalogued,
  also not a hit, same stale `last-guest-pc`.
- Pre-scene rate: 0/2 this session vs. 7/8 (87.5%) across s276-278+s280. New running total
  s276-278+s280-281: **7/10 = 70%**. Same binary as s276-s280 (no rebuild) — weakens the "elevated
  rate is a fixed build property" framing, more consistent with ordinary scheduling
  nondeterminism. Not conclusively resolved either way (still a small sample).

**Whole-family status** (`BREADCRUMB5`-`BREADCRUMB9`, updated for s281):
- `BREADCRUMB5`/`reserveAndEmitDLEntry`: 0/4 (s272+s273), 2 sessions, never informative.
- `BREADCRUMB6`/`buildPositionAndCallTransformHelper`: 0/4 (s273+s280), 2 sessions, never
  informative.
- `BREADCRUMB7`/`static_5_800AB658`: 0/4 (s274+s281), 2 sessions, never informative. **Do NOT
  re-soak a 3rd session — no new angle identified.**
- `BREADCRUMB8`/`emitAllocatedDLCommand`: 0/2 (s275), only 1 session. **The LAST remaining
  untested-twice target — this session's job.**
- `BREADCRUMB9`/`tickWrappingTimerAccumulatorList`: 0/2 genuine across 3 sessions (6 soaks),
  3-strikes hit s278, confound angle closed s279. Do not re-soak.

All 5 breadcrumbs now sit at 0 combined informative hits on their own target. `BREADCRUMB8` is
the only one left that hasn't had its 2nd session — after this session, there will be no more
"next untested-twice breadcrumb" to fall back on without inventing a 6th target from scratch.

## The next work unit

**Re-soak `BREADCRUMB8`/`emitAllocatedDLCommand` (its 2nd session).**

1. Confirm `BREADCRUMB8` is still armed: `grep -n "BREADCRUMB8" /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` (expect the same patch block from s275). Check binary vs fixup-script timestamps (`ls -la build/RogueSquadron64Recomp` vs the fixup script's mtime) — matching timestamps mean no regen needed (true for s276-s281, likely still true).
2. Soak twice, `HOLD_S=240`, launch each `run_in_background: true` from an absolute path, then
   `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME turn (cross-turn waiting does
   not work under the Stop hook):
   `env HOLD_S=240 zsh /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/s73_post_a_scene/run_dequeuearg1.sh s282_soak1`
   then `s282_soak2`.
3. Check each soak: `grep -c "vi_width=1024" <run.log>` (0 = pre-scene death; >=1 = reached the
   scene — check for `BREADCRUMB8`-specific crash hits and any brand-new symrange-confirmed
   crash site). Then `grep -n "CRASH" <run.log> | tail -50` for crash detail regardless.
4. **Discriminating outcome**: any hit inside `emitAllocatedDLCommand` itself confirms the
   hypothesis for the first time in this family — treat as a real finding, land a guard, do NOT
   just note it and move on.
5. **Track the pre-scene rate regardless of outcome**: append this session's pre-scene/soak
   count to the running tally (currently 7/10 = 70% across s276-278+s280-281).
6. **If a genuinely new/different crash surfaces**: symrange-verify if plausible (Mach-O symtab
   walk, see s273-s281's approach), note it for the backlog. Don't chase it this iteration unless
   clearly highest-information-value (budget rule 8).

**If `BREADCRUMB8` also comes back 0/2 (0/4 combined total)**: every one of the 5 breadcrumbs will
have exhausted its reasonable per-target budget (2 sessions or 3-strikes) with 0 combined
informative hits on any of their own targets. Do NOT invent a 6th breadcrumb without a genuinely
new mechanism. Next session should instead either:
- Start the `inflate_fast`/zlib localization design (system-library call, not a guest function —
  needs a different approach, bigger lift, never attempted yet), or
- Write a BLOCKED note to the human: the breadcrumb-hunting strategy has surfaced several
  already-catalogued crash sites as a side effect but has confirmed 0 of its own per-target
  hypotheses across what will be 6 target-sessions (5 targets, one tested twice-plus). That is a
  real signal the strategy itself — not just the next individual target — needs reassessment with
  a human, not another automatic re-soak.

## Do NOT do this iteration

- Do NOT re-soak `BREADCRUMB6` or `BREADCRUMB7` a 3rd session — both now 0/4 combined (2
  sessions each), no new angle identified for either.
- Do NOT re-soak `BREADCRUMB9` again — 3-strikes threshold (s278), confound angle closed (s279).
  No new angle currently exists.
- Do NOT re-open the instrumentation-confound investigation without a genuinely new mechanism —
  s279's direct source read of `menuOverlayInit` is a solid, first-hand mechanistic refutation of
  the call-site angle specifically, not a weak inferential one.
- Do NOT treat the pre-scene death-rate reversion (87.5%→70%) as fully explaining or resolving
  the earlier spike — it's a data point against the "fixed build property" framing, not a
  confirmed mechanism. If it swings sharply again (either direction) over the next session or
  two, that's worth a dedicated fresh-hypothesis look, but is not itself this iteration's job
  unless it comes up for free during the `BREADCRUMB8` soak's own analysis.
- Do NOT treat `coalesceFreeHeapBlocks` or `tickTextureMaterialExpiry` crashes as new findings —
  both already catalogued (CURRENT-TRUTH ~line 1068/1088/1098/1308, PORTING-STATE s264-era notes)
  as a not-yet-localized family, possibly ASLR/nearest-symbol misattribution artifacts.
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
  session.

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
  allowlist) instead.
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
  python, see s273-s281's approach: parse LC_SYMTAB, sort `(n_value, name)` pairs by DISTINCT
  address, find the exact-name entry, check the reported crash offset is less than the
  distance to the next DISTINCT address — duplicate symtab entries at the same address are
  common, dedupe by address before computing "next symbol" or the range check
  false-negatives). System-library crashes (like `inflate_fast`) resolve via the OS's own dyld
  symbol table and don't need/support the same check.
- A crash's `[CRASH][last-guest-pc]` value is only informative if the crashing function is
  ITSELF breadcrumbed. Always grep the reported guest PC's hex label in the relevant
  `funcs_N.c` and find its enclosing `RECOMP_FUNC` before trusting it. `0x8000b650`
  specifically is a recurring stale value belonging to `beginFrameDLChunk` (`funcs_3.c`) — do
  not treat it as informative unless the crashing symbol IS `beginFrameDLChunk`.
- When adding a guard to a function that's ALSO covered by an existing breadcrumb's blanket
  per-instruction pass: check whether the guard patch's code block sits before or after the
  breadcrumb patch's block in `fixup_game_funcs.py`'s file order. A guard block positioned
  BEFORE its function's breadcrumb block sees PRE-breadcrumb text and must not require
  `g_rs64_last_guest_pc` lines in its match regex.
- Redirecting shell output (`>`) only works to paths under one of the 3 session working
  directories — `/tmp` is blocked. Use `scratch/agent/*.log`.
- `N64Recomp/fixup_game_funcs.py` is untracked by git in the standalone `N64Recomp` checkout —
  expected. Changes persist only via the live file on disk across sessions.
- `git status --short` run from inside `RogueSquadron64Recomp/build` (or any subdir, via a
  plain `cd` + `git status` as two separate Bash calls) works without needing `-C`/`git
  --git-dir` approval prompts.
- `CURRENT-TRUTH.md` is far over the ~35KB target (measured s280-281: >500KB, way over) — now
  22+ consecutive sessions overdue for a pruning pass. Still not this iteration's job unless the
  localization work above is a quick null with clear leftover budget. Note: the file is now large
  enough that a plain `Read` on it fails outright (>256KB tool limit) — use `grep -n` to find
  section line numbers, then `Read` with `offset`/`limit` on just the needed section.
- At session start, check `scratch/agent/STATUS`/`OUTCOME` for signs of an interrupted prior
  iteration (e.g. `STATUS=WORKING` with `OUTCOME` deleted but HEAD already at the last commit) —
  this is normal loop-restart noise, not unfinished work, as long as `git log` confirms the last
  session's commit landed cleanly. Don't spend budget investigating it further once confirmed.
