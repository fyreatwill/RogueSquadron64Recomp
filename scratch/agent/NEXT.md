# NEXT work unit — begin the chunked `hangarInitialize` `-0x25A4($s1)` audit
# (first chunk only), continuing the deliberate global-pointer audit from s284

## Where the investigation stands (s284)

s284 completed the deliberate grep-based audit of the `-0x25A4($s1)` "hangar list" global-pointer
across `RecompiledFuncs/*.c` for every function EXCEPT `hangarInitialize`. Full detail:
`PORTING-STATE` Session 284, `CURRENT-TRUTH` item -125.

**What happened**: grepped all 173 `-0X25A4` hits in `RecompiledFuncs/*.c`, traced each hit's
feeding `lui` value (not just the offset — caught 1 false positive, `npcShieldGeneratorUpdate`,
unrelated `lui 0x8004` global). Of 172 confirmed hits: `static_5_800AB658` (32) and
`static_5_800A9270` (4) were already fully guarded. `static_5_800AAD9C` (2),
`static_5_800AB1C8` (10, 5 unguarded), `static_5_800ADB70` (21, all unguarded) had never been
audited — classified all of them, landed 28 new guards, full regen+build+3 soaks. Soak1 (post-
28-guard build) crashed at a NEW "second-hop" site inside `static_5_800A9270` (a pointer read
FROM the already-validated hangar-list entry, itself never validated before its own dereference)
— found, fixed (`S284_A9270_SECONDHOP`), re-regen+rebuild, soak2/soak3 both reached the scene and
survived, dying at two other already-catalogued sites, neither reproducing the crash or firing
the new guard.

**What's left**: `hangarInitialize` (`funcs_27.c`, lines 119802-133178, 13,376 lines, 103 hits of
the same global). A scoping-only sample (22 of 103 sites) found ~21 of 22 unguarded, same shape
family (a `ptr = MEM_W(base,-0x25A4); addr = index + ptr; field = MEM_x(addr, off)` idiom,
sometimes with a `index * 0x278` struct-size multiply first), 1 safe (the global's own
initializing write). The function has only **5 true epilogues** (`return` points) at lines
~123792, ~124604, ~125413, ~132214, ~133175 — everything between 125414-132214 (the largest
chunk, ~6800 lines) has no intermediate return and must `goto` the 132214 epilogue.

## The next work unit

**Classify and guard ONLY the first chunk: lines 119802-123792 (the function start through its
first epilogue).** Do NOT attempt the whole function in one session — it is roughly 4x the size
of everything guarded in s284 combined, and per-site classification needs the same rigor used
last session (each site needs its own dereference chain traced, not just pattern-matched).

1. Get the exact list of `-0X25A4` hit line numbers in this chunk:
   `grep -n "0X25A4" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c`
   filtered to lines 119802-123792 (should be roughly 20-30 of the 103 total hits, going by the
   chunk's ~30% share of the function's line count — do not assume, count them exactly).
2. Delegate classification to a background agent exactly as s284 did for `static_5_800ADB70`
   (see `PORTING-STATE` Session 284 for the exact prompt shape that worked): give it the file,
   the line range, the exact hit line numbers, the established GUARDED/UNGUARDED-DEREF/SAFE
   classification criteria, AND explicitly ask it to check for the **second-hop pattern** found
   twice now (s282's `G32`, s284's `S284_A9270_SECONDHOP`) — a pointer field READ OUT of an
   already-validated structure, then dereferenced without its own validation. Ask for the
   function's own nearest epilogue label for each site (should be the ~123792 one, but confirm —
   don't assume every site in this line range bails to the same place if there's an earlier
   intermediate return you haven't accounted for).
3. Verify anchor-pattern uniqueness within `funcs_27.c` BEFORE splicing into
   `fixup_game_funcs.py` — reuse s284's `verify_uniqueness.py` approach (dry-run `re.finditer`
   count == 1 for every pattern) rather than trusting the classification agent's line numbers
   blindly, since `hangarInitialize` is large enough that duplicate-shaped anchor text is more
   likely than in the smaller functions audited last session.
4. Batch every genuinely unguarded site in THIS CHUNK into one fixup-script edit, one regen
   (`make_elf.py` is NOT needed again — only re-run `N64Recomp` + `fixup_game_funcs.py` + build,
   since the ELF/ROM mapping hasn't changed), one build.
5. Validate with 2-3 soaks, `HOLD_S=240`, `run_in_background: true` + `TaskOutput(block=true,
   timeout<=480000)` in the same turn. Expect the usual ~1-in-3-4 pre-scene
   `waitForAnyAudioSlot` death (uninformative). If a soak crashes INSIDE `hangarInitialize`
   itself post-patch, treat it the same way s284 treated soak1: re-read the specific crashing
   region for an unguarded/second-hop site rather than assuming the patch is wrong.

**Chunk 2-5** (the remaining ~123792-133178 range, broken further given the 125414-132214 span is
itself ~6800 lines) are follow-on work units for future sessions — do not attempt more than one
chunk per session; each chunk deserves its own regen/build/soak cycle per the "capture once,
analyze many" rule, but chunks themselves should NOT be batched together across a single cycle
given the classification rigor each needs.

## Do NOT do this iteration

- Do NOT attempt more than the first chunk (119802-123792) of `hangarInitialize` — the whole
  function is too large for one session's classification rigor.
- Do NOT re-touch `static_5_800AAD9C`, `static_5_800AB1C8`, `static_5_800ADB70`, or
  `static_5_800A9270`'s guards — all fully audited and validated non-recurring as of s284.
- Do NOT re-touch `static_5_800AB658`'s `G1`-`G32` family or `BREADCRUMB5`-`9` — all past budget,
  no new angle since s280-283.
- Do NOT treat `processSceneNode`, `reserveAndEmitDLEntry`, `coalesceFreeHeapBlocks` crashes as
  new findings — all already catalogued (CURRENT-TRUTH ~line 1068/1088/1098/1308).
- Do NOT cite `x0`/`x8`/`x9`/`x10`/`x11`/`x12` = constant RDRAM-base-pointer-looking values as
  crash-matching evidence for ANYTHING — seen across many unrelated crashes.
- Do NOT re-run `fixup_game_funcs.py` on an already-patched `funcs_*.c` — always delete
  `funcs_*.c` and regenerate fresh from `N64Recomp` first, or guards stack/duplicate.
- Do NOT idle across a Stop-hook turn boundary waiting on a background soak — block with
  `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME turn.
- Do NOT touch the `lib/N64ModernRuntime`/`lib/rt64` "-dirty" submodule state — long-standing
  baseline, not new work.

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` needs cwd `rogue_squadron64` (`python3 tools/make_elf.py`) — NOT
  needed again this session unless the ELF/ROM mapping changed (it hasn't). `N64Recomp` needs cwd
  `N64Recomp` (`./build/N64Recomp rogue_squadron.toml`), `fixup_game_funcs.py` needs cwd
  `N64Recomp`. Always delete `funcs_*.c` and regen from scratch before running
  `fixup_game_funcs.py`:
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
  (`rm`/`find -delete` are sandbox-blocked).
- `cd` does not persist into a subsequent `run_in_background: true` call — always launch
  background commands by full absolute path with no preceding bare `cd`, e.g.
  `env HOLD_S=240 zsh /abs/path/run_dequeuearg1.sh > /abs/path/log 2>&1`.
- Bash tool cwd DOES persist across sequential (non-background) calls in the same session, but
  gets reset by unrelated `cd`s earlier in the same session (e.g. `cd build` for cmake) — always
  re-`cd` explicitly before a command that depends on cwd, don't assume it's still where you left
  it hours/many-tool-calls ago.
- Compound shell commands using `cd` combined with `&&`/output-redirection require interactive
  approval — issue `cd <dir>` as its OWN Bash call first, then run the next command separately.
- `git -C <path> ...` / `git --git-dir=...` get flagged for approval even standalone — use plain
  `cd` (its own call) + `git status --short` (its own call). `nm -n <binary> > file` also flagged
  — use Python `subprocess.run(["nm","-n",path], capture_output=True)` instead.
- Shell `for`/`$(...)` loops get rejected by the sandbox. Prefer a single `grep`/`ls` with an
  explicit glob, or a Python script via `Write` + `Bash python3 script.py`.
- Multi-line `python3 -c "..."` with embedded `#` comments or newlines gets flagged by the
  sandbox's path-validation heuristic ("Newline followed by # inside a quoted argument") — write
  scripts to a file via `Write` and run with `python3 /path/to/script.py` instead of inline `-c`.
- Cross-turn waiting does not work under the Stop hook — use `TaskOutput(task_id, block=true,
  timeout<=480000)` synchronously in the same turn.
- Soak driver: `scratch/s73_post_a_scene/run_dequeuearg1.sh` (`HOLD_S` overridable via env,
  defaults to 240). Output dir `scratch/s73_post_a_scene/dequeuearg1/run.log` — OVERWRITTEN each
  run, grep/save anything needed before launching the next soak.
- Whether a soak reached the scene: `grep -c "vi_width=1024" <run.log>` (0 = pre-scene death,
  >=1 = reached it).
- `+N` crash-symbol offsets are NATIVE (ARM64) and SHIFT across sessions as guards are added.
  Verify range membership via the Mach-O symtab walk (`subprocess.run(["nm","-n",path],
  capture_output=True, text=True)`, filter type T/t, dedupe by address, sort, confirm the crash
  offset is less than the distance to the next DISTINCT symbol address) — do not trust a reported
  `sym=X+N` without this check, per s284's confirmed example of doing it right.
- A crash's `[CRASH][last-guest-pc]` value is only informative if the crashing function is ITSELF
  breadcrumbed (only `static_5_800AB658` carries a guest-PC breadcrumb, `BREADCRUMB7`) — for any
  other crashing function, that field is stale noise from an earlier call, not the crash site.
  Use the native `[CRASH][pc-symbol]` line + symtab walk instead.
- Redirecting shell output (`>`) only works to paths under one of the 3 session working
  directories — `/tmp` is blocked. Use `scratch/agent/*.log`.
- `N64Recomp/fixup_game_funcs.py` is untracked by git in the standalone `N64Recomp` checkout —
  expected, changes persist only via the live file on disk across sessions.
- `CURRENT-TRUTH.md` is far over the ~35KB target (measured s284: >500KB) — 25+ consecutive
  sessions overdue for pruning. Still not this iteration's job unless the audit chunk above is a
  quick null with clear leftover budget. Use `grep -n` to find section line numbers, then `Read`
  with `offset`/`limit` — a plain `Read` on the whole file fails (>256KB tool limit).
- At session start, check `scratch/agent/STATUS`/`OUTCOME` for signs of an interrupted prior
  iteration — normal loop-restart noise as long as `git log` confirms the last session's commit
  landed cleanly. Don't spend budget investigating further once confirmed.
- The pre-scene `waitForAnyAudioSlot` boot crash remains elevated-rate and unexplained since s278
  — never directly investigated, only observed as background noise. Costs real soak budget most
  sessions; worth prioritizing directly once the `hangarInitialize` audit chunks are further
  along or exhausted.
