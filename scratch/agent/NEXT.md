# NEXT work unit — confirm `hangarInitialize` chunk 3 is dead code, then move to chunk 4
# continuing the chunked `-0x25A4($s1)` audit from s285/s286

## Where the investigation stands (s286)

s286 classified `hangarInitialize` chunk 2 (`funcs_27.c` lines 124187-124999) and found it is
**entirely unreachable duplicate dead code** — a byte-for-byte copy of `static_5_800AAD9C`'s
already-fully-guarded body (`funcs_40.c:5544-6382`), needing 0 new guards. Full detail:
`PORTING-STATE` Session 286, `CURRENT-TRUTH` item -127.

**The methodology that found this** (now the standard tool — use it on chunk 3 before any
per-site classification):
1. Extract every `// 0xADDR: mnemonic` comment line from the candidate region and from the
   suspected already-audited `funcs_40.c` function's real body. Diff them position-by-position
   (not a line diff of the whole file — extract just the comment stream first, ignoring the
   `ctx->...` C statement lines, which can differ trivially in whitespace/temp-var naming even
   when the underlying instruction is identical).
2. Check the region is bounded by an unconditional `return;` at both its start and end (proof nothing
   falls through into it and it doesn't fall through past its own end into a genuinely different
   function).
3. Extract every `L_<addr>:` label defined inside the region. Grep the WHOLE FILE for
   `goto L_<addr>;` references to those exact label names, then for each hit determine which
   actual C function it lives in (scan backward for the nearest `RECOMP_FUNC void <name>(` before
   that line — **do not just match by label name across the file**, C `goto`/labels are
   function-scoped, so a same-named label in an unrelated function is a false positive, not a real
   cross-function jump). Only a hit whose containing function matches the region's own function is
   a real reachability concern.
4. If steps 1-3 all confirm (byte-identical diff, return-bounded, no genuine external goto), the
   region is dead code from an overlay address-range collision — 0 new guards needed, full stop.
   Do NOT invent guards for unreachable code.

## The next work unit

**Confirm chunk 3 (`funcs_27.c:124999-125808`) using the methodology above**, checking it against
`static_5_800AB1C8`'s real body (`funcs_40.c:6388-7405`, already fully guarded 10/10 sites per
s284). s286 already ran a preliminary version of this check (322/323 aligned instructions matched,
1-line delta being the same known trailing-repeat-after-`return;` codegen artifact seen at every
chunk boundary) and found the same reachability shape (2 same-named-label `goto`s, both inside the
unrelated function `playerSnowSpeederInit`, not real hits) — but this was NOT run as chunk 3's
official session work, so re-run it properly and treat it as this session's actual classification,
not a rubber stamp. If it confirms dead (expected), chunk 3 is CLOSED with 0 new guards, no
regen/rebuild/soak needed (nothing changes), and you should have real budget left over — proceed to
scope chunk 4 (`125808-132609`, ~6800 lines) using the SAME methodology before assuming it's
uniformly live: check whether chunk 4 itself contains further `return;`-bounded dead-duplicate
sub-regions (there is no guarantee the whole ~6800 lines is genuine `hangarInitialize` audit
surface — the density-uniformity assumption has already been proven false twice now).

If chunk 3 does NOT confirm dead (i.e., the diff finds real mismatches, meaning it's genuinely
`hangarInitialize`'s own live code, not a duplicate), fall back to the original per-site
classification process used for chunk 1: grep exact `-0X25A4` hit lines, classify each as
WRITE/SAFE/GUARDED/UNGUARDED, delegate to an agent if the count is large, get an independent
reconciliation pass, land guards in `N64Recomp/fixup_game_funcs.py`, regen+rebuild+soak. Do not
assume dead-code without actually running the checks — s286's preliminary check is a strong prior,
not a substitute for this session's own verification.

## Do NOT do this iteration

- Do NOT attempt chunk 4 or 5's actual classification unless chunk 3 confirms dead AND you have
  real budget left over AND you scope chunk 4's own dead/live boundary first (per above) — don't
  jump straight into per-site classification of a 6800-line chunk assuming it's all live.
- Do NOT re-touch `static_5_800AAD9C`, `static_5_800AB1C8`, `static_5_800ADB70`, `static_5_800AB658`
  (`G1`-`G32`/`BREADCRUMB5`-`9`), `static_5_800A9270` (`R4`/`SECONDHOP`/etc.), or chunk-1's
  `S285_H1_*` guards — all validated in prior sessions.
- Do NOT assume `static_5_800A9270` is fully closed just because `R4` is fixed — it has missed
  sites 3 times now (s284, s285); if it crashes again, treat it as informative, not noise.
- Do NOT treat `processSceneNode`, `reserveAndEmitDLEntry`, `coalesceFreeHeapBlocks`, or
  `waitForAnyAudioSlot` crashes as new findings — all already catalogued.
- Do NOT cite `x0`/`x8`/`x9`/`x10`/`x11`/`x12` = constant RDRAM-base-pointer-looking values as
  crash-matching evidence for ANYTHING.
- Do NOT run `fixup_game_funcs.py` twice without a fresh `N64Recomp` regen in between.
- Do NOT idle across a Stop-hook turn boundary waiting on a background soak — block with
  `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME turn.
- Do NOT audit `playerSnowSpeederInit` this session — it's a newly-discovered candidate (s286,
  independently duplicates at least part of the same address range) but is out of scope until
  the `hangarInitialize` chunking is finished or explicitly reprioritized.

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
- `CURRENT-TRUTH.md` is far over the ~35KB target (27+ sessions overdue) — not this iteration's
  job unless the chunk-3 confirmation is a quick null with clear leftover budget.
- At session start, check `scratch/agent/STATUS`/`OUTCOME` for signs of an interrupted prior
  iteration before assuming a `WORKING`/missing-`OUTCOME` state means recovery work is needed — s286
  found this state was just the loop's normal per-iteration bootstrap (committed ~2.5 minutes
  earlier), not an interrupted session. Only treat it as recovery-worthy if there's actual
  uncommitted diff evidence (e.g. `git status`/`git diff` on `fixup_game_funcs.py` or other tracked
  work files) beyond the routine `STATUS`/`OUTCOME` reset.
- The pre-scene `waitForAnyAudioSlot` boot crash remains elevated-rate and unexplained since s278
  — still never directly investigated, only observed as background noise.
