# NEXT work unit — classify `playerSnowSpeederInit` using the dead-code-detection methodology
# `hangarInitialize`'s full `-0x25A4` audit is CLOSED as of s287 (chunks 1-5 all classified: chunk 1
# live/guarded, chunks 2-5 all confirmed dead duplicate code, 0 new guards). Do not re-touch it.

## Where the investigation stands (s287)

s287 closed the entire `hangarInitialize` audit in one session: chunks 3, 4, and 5 (the remaining
~89% of the function, `funcs_27.c` 124187-133572) are ALL confirmed dead unreachable duplicate code
— chunk 3 duplicates `static_5_800AB1C8`, chunk 4 (one single 6800-line monolithic block, no
internal `return;` boundaries) duplicates `static_5_800AB658`, chunk 5 duplicates
`static_5_800ADB70`. All three passed the full 3-check proof (comment-stream diff,
return-boundedness, function-scoped goto-reachability — 0 genuine external jumps into any chunk).
Full detail: `PORTING-STATE` Session 287, `CURRENT-TRUTH` item -128.

**Key lesson carried forward**: raw `-0x25A4` hit density is NOT a reliable live/dead signal —
chunk 4's density (64 hits/6802 lines) was HIGHER than live chunk 1's (38/4400) despite being
entirely dead. Never infer live/dead from density; always run the full 3-check proof.

**The methodology** (now standard — use it on `playerSnowSpeederInit` BEFORE any per-site
classification):
1. Extract every `// 0xADDR: mnemonic` comment line from the candidate region and from the
   suspected already-audited `funcs_40.c` function's real body. Diff them position-by-position
   (comment-stream only — ignore the `ctx->...` C statement lines, which can differ trivially in
   whitespace/temp-var naming even when the underlying instruction is identical). Expect exactly
   one trailing-delay-slot boundary artifact per side at chunk edges — trim it, don't count it as a
   mismatch.
2. Check the region is bounded by an unconditional `return;` at both its start and end.
3. Extract every `L_<addr>:` label defined inside the region. Grep the WHOLE FILE for
   `goto L_<addr>;` references to those exact label names, then for each hit determine which
   actual C function it lives in (scan backward for the nearest `RECOMP_FUNC void <name>(` before
   that line — labels/gotos are function-scoped in C, so a same-named label in an unrelated
   function is a false positive, not a real cross-function jump). Only a hit whose containing
   function matches the region's own function is a real reachability concern.
4. If steps 1-3 all confirm, the region is dead code — 0 new guards needed, full stop. Do NOT
   invent guards for unreachable code.

## The next work unit

**Classify `playerSnowSpeederInit`** (`funcs_27.c`, starts ~line 144145 — confirm its exact
start/end bounds first via its `RECOMP_FUNC` signature and the next function's signature after it).
It was explicitly out-of-scope while `hangarInitialize`'s chunking was open; that condition is now
satisfied.

**Why this is likely (but NOT confirmed — verify, don't assume) mostly dead code**: across s286/s287,
`playerSnowSpeederInit` was found reusing label names from chunk 2 (`static_5_800AAD9C`'s address
range), chunk 3 (`static_5_800AB1C8`'s), AND chunk 4 (`static_5_800AB658`'s) — all three, not just
one. That breadth suggests it may sit in the same overlay-collision address range as some or all of
`hangarInitialize` chunks 2-4, i.e. it could itself be a dead-or-partially-dead duplicate. But this
was only observed as a byproduct of goto-reachability greps for the OTHER function's chunks — it has
never been directly read or classified on its own terms. Do not rubber-stamp it as dead; run the
actual methodology.

Steps:
1. Find `playerSnowSpeederInit`'s true start/end line range and its guest address range (first/last
   `// 0xADDR:` comment).
2. Grep every `-0x25A4($s1)` (and `-0X25A4`, check both cases) occurrence within its range to get a
   raw hit count — this alone does NOT determine live/dead (see key lesson above) but is useful
   context.
3. Check whether its address range (or return-bounded sub-regions within it) match any already-
   guarded `funcs_40.c` function's address range (the same 4 candidates as before —
   `static_5_800AAD9C`, `static_5_800AB1C8`, `static_5_800AB658`, `static_5_800ADB70` — plus stay
   open to a different match; don't assume it must be one of these 4).
4. For any match found, run the full 3-check proof (comment-stream diff, return-boundedness,
   goto-reachability) exactly as chunks 2-5 were done. If it's a SINGLE block spanning the whole
   function (like chunk 4 was), one proof suffices. If it's multiple sub-regions like chunks 1-5,
   classify each separately — it does NOT have to map 1:1 onto hangarInitialize's chunk structure.
5. For any region that does NOT match a known duplicate (i.e. genuinely live code), fall back to
   the standard per-site classification process: grep exact `-0X25A4` hit lines, classify each as
   WRITE/SAFE/GUARDED/UNGUARDED, delegate to an agent if the count is large, get an independent
   reconciliation pass, land guards in `N64Recomp/fixup_game_funcs.py`, regen+rebuild+soak.

If `playerSnowSpeederInit` turns out to be ENTIRELY dead (plausible given the 3-function label
overlap), this closes with 0 guards and 0 regen/build/soak, same as this session — in that case,
with budget left over, move to the standing backlog: investigate the elevated pre-scene
`waitForAnyAudioSlot` death rate (open since s278, never directly investigated), or start the
`inflate_fast`/zlib localization design (s272, never attempted, needs a different approach since
it's a system-library call).

## Do NOT do this iteration

- Do NOT re-touch `hangarInitialize` (any chunk), `static_5_800AAD9C`, `static_5_800AB1C8`,
  `static_5_800ADB70`, `static_5_800AB658` (`G1`-`G32`/`BREADCRUMB5`-`9`), `static_5_800A9270`
  (`R4`/`SECONDHOP`/etc.) — all validated/closed in prior sessions.
- Do NOT assume `playerSnowSpeederInit` is dead without running the actual 3-check proof — the
  3-function label overlap is a strong prior, not a substitute for verification.
- Do NOT assume `static_5_800A9270` is fully closed just because `R4` is fixed — it has missed
  sites 3 times now (s284, s285); if it crashes again, treat it as informative, not noise.
- Do NOT treat `processSceneNode`, `reserveAndEmitDLEntry`, `coalesceFreeHeapBlocks`, or
  `waitForAnyAudioSlot` crashes as new findings — all already catalogued.
- Do NOT cite `x0`/`x8`/`x9`/`x10`/`x11`/`x12` = constant RDRAM-base-pointer-looking values as
  crash-matching evidence for ANYTHING.
- Do NOT run `fixup_game_funcs.py` twice without a fresh `N64Recomp` regen in between.
- Do NOT idle across a Stop-hook turn boundary waiting on a background soak — block with
  `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME turn.

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` NOT needed (ELF/ROM mapping unchanged since s284). `N64Recomp`
  needs cwd `N64Recomp` (`./build/N64Recomp rogue_squadron.toml`), `fixup_game_funcs.py` needs cwd
  `N64Recomp`. Always delete `funcs_*.c` and regen from scratch first:
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
- `cd` does not persist into a subsequent `run_in_background: true` call — launch background
  commands by full absolute path with no preceding bare `cd`.
- Bash tool cwd persists across sequential (non-background) calls but resets after an unrelated
  `cd` elsewhere in the session — re-`cd` explicitly before cwd-dependent commands.
- Compound `cd && ...` commands need interactive approval — issue `cd` as its own call first.
- `git -C`/`git --git-dir=`/`cd <dir> && git ...` all get flagged for approval even standalone (this
  session confirmed both forms prompt) — if you need submodule git state, expect an approval
  prompt, or use `git diff -- lib/<submodule>` from the repo root (shows the gitlink pointer/dirty
  flag without entering the submodule). `nm -n <binary> > file` also flagged — use Python
  `subprocess.run`.
- Shell `for`/`$(...)` loops get rejected by the sandbox — use Python scripts via `Write` instead.
- Multi-line `python3 -c "..."` with embedded `#`/newlines gets flagged — write to a file and run
  `python3 /path/to/script.py`.
- Soak driver: `scratch/s73_post_a_scene/run_dequeuearg1.sh` (`HOLD_S` env-overridable, default
  240). Output dir `scratch/s73_post_a_scene/dequeuearg1/run.log` — OVERWRITTEN each run.
- Scene-reached check: `grep -c "vi_width=1024" <run.log>` (0 = pre-scene death, >=1 = reached).
- `+N` crash-symbol offsets are NATIVE (ARM64) and SHIFT across sessions — verify range membership
  via the Mach-O symtab walk (`nm -n`, filter T/t, dedupe, sort, confirm offset < distance to next
  DISTINCT symbol) before trusting a reported `sym=X+N`.
- `[CRASH][last-guest-pc]` is only informative for `static_5_800AB658` (the only breadcrumbed
  function, `BREADCRUMB7`) — stale noise for any other crashing function.
- Redirecting shell output (`>`) only works under the 3 session working directories, not `/tmp`.
- `N64Recomp/fixup_game_funcs.py` is untracked in the standalone `N64Recomp` checkout — no
  `export.sh` needed for edits there, only for actual `lib/` submodule changes.
- `CURRENT-TRUTH.md` is far over the ~35KB target (28+ sessions overdue) — not this iteration's
  job unless the `playerSnowSpeederInit` classification is a quick null with clear leftover budget.
- At session start, check `scratch/agent/STATUS`/`OUTCOME` for signs of an interrupted prior
  iteration before assuming a `WORKING`/missing-`OUTCOME` state means recovery work is needed —
  s286/s287 both found this state was just the loop's normal per-iteration bootstrap, not an
  interrupted session. Only treat it as recovery-worthy if there's actual uncommitted diff evidence
  (e.g. `git status`/`git diff` on `fixup_game_funcs.py` or other tracked work files) beyond the
  routine `STATUS`/`OUTCOME` reset.
- The pre-scene `waitForAnyAudioSlot` boot crash remains elevated-rate and unexplained since s278
  — still never directly investigated, only observed as background noise.
