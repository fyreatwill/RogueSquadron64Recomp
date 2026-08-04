# NEXT work unit — start the `inflate_fast`/zlib investigation (s272, never attempted)

Both standing backlog items are now CLOSED: the `-0x25A4($s1)` hangar-list-pointer audit lineage
(s283-288, `CURRENT-TRUTH` item -129) and the elevated pre-scene `waitForAnyAudioSlot` death-rate
investigation (s289, `CURRENT-TRUTH` item -130, closed as a non-finding — the rate reverted 8
sessions ago and has stayed reverted). Do not re-open either without a NEW discriminating signal.

## Where the investigation stands (s289)

s289 quantified the `waitForAnyAudioSlot` pre-scene death rate across s281-288 (offline analysis,
no soaks spent): 2 pre-scene deaths / 16 soaks = 12.5%, LOWER than the original pre-elevation
baseline (21%, s270-275). The "elevated since s278" framing was accurate when written but the
elevated window (s276-278+280, 87.5%) had already fully reverted by s281 — closed as a non-finding.
Full detail: `PORTING-STATE` Session 289, `CURRENT-TRUTH` item -130.

**Free bonus finding from s289, changes the shape of this work unit**: `inflate_fast` is NOT a
system-library call, contrary to every prior mention in `CURRENT-TRUTH.md` since s272 (an unverified
assumption that propagated for 17 sessions without being checked). It's a full `RECOMP_FUNC` with
guest-MIPS-address comments (`N64Recomp/RecompiledFuncs/funcs_7.c:13553`) — the original N64 game
embeds its own compiled zlib. `funcs_1.c`, `funcs_7.c`, and `funcs_34.c` all contain `inflate*`
`RECOMP_FUNC`s (`inflateInit_`, `inflate_recomp`, `inflate_blocks`, `inflate_fast`, `inflate_flush`,
etc. — grep `inflate` across `RecompiledFuncs/*.c` for the full list). **This means the standard
breadcrumb/guard-patch recipe used throughout s254-288 for every other crash site applies directly
here** — no novel host-hook/wrap instrumentation design needed, despite what every older
`CURRENT-TRUTH.md` mention of this item implies.

## What's already known (do not re-derive, build on it)

- Only 1 crash observation on record: s272 soak2, `si_addr=0x380000003`, native
  `sym=inflate_fast+5344`. `last-guest-pc` at the time of that crash was stale (pointed at
  `beginFrameDLChunk`, confirmed via grep — uninformative, don't re-cite it as if it were the crash
  site). Full detail: `CURRENT-TRUTH` item around line ~1271 (s272 write-up), `PORTING-STATE`
  Session 272.
- `inflate_fast` is called from `inflate_blocks` (`funcs_7.c:12351`). `inflate_recomp` (the
  top-level entry point, `funcs_1.c:2267`/`:2428`) calls into the `inflate_blocks`/`inflate_fast`
  chain — these 2 call sites in `funcs_1.c` are the guest-code callers into the whole zlib chain,
  worth checking what THEY pass in (buffer pointers, sizes) since a bad caller-supplied argument
  reaching an unguarded zlib-internal dereference fits this investigation's dominant bug shape
  (unguarded pointer chase from a caller-controlled value) just as well as an internal zlib bug
  would.
- `si_addr=0x380000003` (low, non-RDRAM-looking address) is consistent with an uninitialized or
  garbage pointer/length value reaching a dereference or array index — the same "unguarded
  pointer/index, no `0x80000000`-`0x80800000` range check" shape behind every guard landed in this
  investigation since s130-ish. Don't assume this without verifying though — actually read the code
  around the crash offset first.

## Steps

1. **Source-read `inflate_fast`** (`N64Recomp/RecompiledFuncs/funcs_7.c:13553`, get the actual
   current line count via `grep -n "^RECOMP_FUNC" funcs_7.c` for the next function's start to bound
   it) for the standard unguarded-dereference shape (a pointer or index reaching a `MEM_*` access
   with no preceding `0x80000000`-`0x80800000`-style range check, or an unchecked array/buffer
   index). This function is large (zlib's core decompression loop) — expect it to take real reading
   time; don't rush past sections.
2. Also read the 2 `funcs_1.c` call sites (`:2267`, `:2428`, inside `inflate_recomp`) and the
   `inflate_blocks` call site (`funcs_7.c:12351`) for what they pass into the chain — a bad argument
   from the caller is as plausible a root cause as an internal zlib bug.
3. If a genuinely unguarded dereference is found: land a guard in `N64Recomp/fixup_game_funcs.py`
   using the same established recipe (`U32(ctx->rN)` range check, bail to the function's own
   epilogue — find it by reading to the closing brace, same as every guard landed s130-288), verify
   the anchor regex is unique in its file before patching, full regen pipeline
   (`make_elf.py` → delete `funcs_*.c` → `N64Recomp` → `fixup_game_funcs.py` → `cmake --build`), then
   2-3 soaks for non-recurrence validation (this crash is rare — only 1 observation ever — so
   non-recurrence over a couple of soaks is the same validation bar used throughout this
   investigation, not a strict positive-control requirement given the low base rate).
4. If the source-read finds nothing obviously wrong (zlib is well-tested upstream code; the bug may
   be in how the recompiler translated it, or in caller-supplied bad state rather than zlib itself),
   that's a legitimate outcome — write up what was checked and ruled out, and reassess: possibly a
   breadcrumb (last-guest-pc tracking, same mechanism as `BREADCRUMB5`-`9`) scoped to `inflate_fast`
   specifically would help localize a 2nd observation before attempting a fix blind.

## Do NOT do this iteration

- Do NOT re-open the `-0x25A4($s1)` audit lineage or the `waitForAnyAudioSlot` elevated-rate
  investigation without a NEW discriminating signal — both closed (s288, s289 respectively).
- Do NOT assume `inflate_fast` needs a host-side hook/wrap approach — it's recompiled guest code,
  confirmed by s289's direct source read. If you find yourself designing a host intercept, stop and
  re-read `funcs_7.c:13553` first.
- Do NOT treat `processSceneNode`, `reserveAndEmitDLEntry`, `coalesceFreeHeapBlocks`,
  `tickTextureMaterialExpiry` crashes as new findings — all already catalogued, unrelated crash
  families.
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
- `git -C`/`git --git-dir=`/`cd <dir> && git ...` all get flagged for approval even standalone, and
  in a non-interactive/autonomous session that approval is NOT available (confirmed s289: both
  forms blocked outright, no prompt resolvable) — do not spend time retrying these forms for
  submodule git state; treat the dirty-submodule baseline as already-established fact from prior
  sessions' direct confirmations (s279, s280, s282, s284, s285) instead of re-attempting to verify
  it each session. `nm -n <binary> > file` also flagged — use Python `subprocess.run`.
- Shell `for`/`$(...)` loops get rejected by the sandbox — use Python scripts via `Write` instead.
- Multi-line `python3 -c "..."` with embedded `#`/newlines gets flagged — write to a file and run
  `python3 /path/to/script.py`.
- Redirecting shell output (`>`) only works under the 3 session working directories
  (`RogueSquadron64Recomp`, `N64Recomp`, `rogue_squadron64`), NOT `/tmp` — writes to `/tmp` are
  blocked outright.
- Soak driver: `scratch/s73_post_a_scene/run_dequeuearg1.sh` (`HOLD_S` env-overridable, default
  240). Output dir `scratch/s73_post_a_scene/dequeuearg1/run.log` — OVERWRITTEN each run, so capture
  the crash symbol out of it into a session note before the next soak clobbers it.
- Scene-reached check: `grep -c "vi_width=1024" <run.log>` (0 = pre-scene death, >=1 = reached).
- `+N` crash-symbol offsets are NATIVE (ARM64) and SHIFT across sessions — verify range membership
  via the Mach-O symtab walk (`nm -n`, filter T/t, dedupe, sort, confirm offset < distance to next
  DISTINCT symbol) before trusting a reported `sym=X+N`.
- `[CRASH][last-guest-pc]` is only informative for `static_5_800AB658` (the only breadcrumbed
  function, `BREADCRUMB7`) — stale noise for any other crashing function.
- `N64Recomp/fixup_game_funcs.py` is untracked in the standalone `N64Recomp` checkout — no
  `export.sh` needed for edits there, only for actual `lib/` submodule changes.
- `CURRENT-TRUTH.md` is far over the ~35KB target (30+ sessions overdue) — not this iteration's job
  unless the `inflate_fast` investigation is a quick null with clear leftover budget.
- At session start, check `scratch/agent/STATUS`/`OUTCOME` for signs of an interrupted prior
  iteration before assuming a `WORKING`/missing-`OUTCOME` state means recovery work is needed — this
  has repeatedly turned out to be just the loop's normal per-iteration bootstrap, not an interrupted
  session. Only treat it as recovery-worthy if there's actual uncommitted diff evidence (e.g.
  `git status`/`git diff` on `fixup_game_funcs.py` or other tracked work files) beyond the routine
  `STATUS`/`OUTCOME` reset. The `lib/N64ModernRuntime`/`lib/rt64` "-dirty" gitlink markers are the
  same long-standing baseline every session has seen — not new, not worth re-verifying each time.
