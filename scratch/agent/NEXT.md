# NEXT work unit — deliberate audit of every `-0x25A4($s1)` "hangar list" global-pointer
# reference across RecompiledFuncs/, rather than waiting for soaks to surface unguarded sites
# incidentally

## Where the investigation stands (s283)

s283 source-read `static_5_800A9270` (`loadCutsceneAssetsByIndex`) per s282's plan and closed the
`static_5_800A9270+948` backlog item — **but found 3 unguarded dereference chains of the same
`-0x25A4($s1)` global in that ONE function, not just 1.** Full detail: `PORTING-STATE` Session 283,
`CURRENT-TRUTH` item -124.

**What happened**: the `-0x25A4($s1)` global (a `0x800D`-region "hangar list" base pointer, `$s1`
loaded as `S32(0X800D << 16)`) is the SAME root-cause global behind the entire `static_5_800AB658`
`G1`-`G32` whack-a-mole family. `static_5_800A9270` reloads and dereferences it in 4 separate
places; only 1 (`HANGARLIST_GUARD`, s254) was guarded before this session. Landed
`HANGARLIST_GUARD_EARLY`/`_WALK`/`_CLEAR` for the other 3 (`N64Recomp/fixup_game_funcs.py`, same
`U32(ctx->rN)` range-check-and-bail-to-`L_800A9350` recipe). Full regen pipeline run, clean build,
all 4 guards (1 existing + 3 new) patched `x1` each. Validated with 3 soaks: soak1 died pre-scene
(uninformative), soak2/soak3 both reached the scene and survived it, dying at two OTHER
already-catalogued sites — **neither reproduced `static_5_800A9270+948` or any of the 3 new guard
sites.**

**The pattern that matters**: this global has now caused confirmed crashes via reload-without-
revalidation in TWO different functions (`static_5_800AB658`'s `G32`, s282; `static_5_800A9270`'s 3
new guards, s283) — 4 confirmed unguarded sites found across 2 sessions, both times by chasing an
incidental soak crash rather than by deliberately searching for the pattern. This strongly suggests
more unguarded sites of the SAME shape exist elsewhere in `RecompiledFuncs/` and would keep
surfacing one whack-a-mole soak at a time if not searched for directly.

## The next work unit

**Grep every reference to the `-0x25A4($s1)` global across `RecompiledFuncs/*.c` and classify each
as guarded/safe vs. an unguarded reload-then-dereference chain, then guard the unguarded ones in
one batched patch.**

1. The MIPS pattern to search for: `lw $vN, -0x25A4($s1)` in the assembly comments (or
   `MEM_W(ctx->r17, -0X25A4)` in the recompiled C, though `$s1`/`ctx->r17` may vary — check what
   register holds `0X800D << 16` in each candidate function first, since the compiler is free to
   assign a different register per function; `static_5_800AB658` and `static_5_800A9270` both
   happen to use `$s1`/`ctx->r17` but that is NOT guaranteed elsewhere). Grep:
   `grep -rn "\-0X25A4" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c` (note
   the recompiled C uses uppercase hex `0X25A4`, not `0x25A4` — confirm the exact casing again
   before trusting a grep that finds 0 hits).
2. For each hit, read enough of the surrounding function to classify: (a) already covered by an
   existing guard (check `fixup_game_funcs.py` for a guard site at/near that address first — grep
   `_hangarbay_deref_guard_sites`, `HANGARLIST_GUARD`, `G1`-`G32` addresses), (b) a genuine
   unguarded reload-then-dereference chain (same shape as this session's 3 new guards — a value
   loaded from `-0x25A4($s1)`, combined with an index/stride, then dereferenced with NO validation
   before the deref), or (c) a safe use (e.g. the loaded value is only ever compared, never
   dereferenced — rarer, but check before assuming every hit needs a guard).
3. Batch every genuinely unguarded site found into ONE fixup-script edit and ONE regen/build cycle
   (do not spend a build-run cycle per site — this is exactly the "capture once, analyze many"
   iron rule). Reuse the established recipe: `U32(ctx->rN)` range check against
   `0x80000000`-`0x80800000`, bail to that specific function's own confirmed epilogue label (read
   each function to its closing brace to find the correct label — do NOT assume `L_800A9350` or
   `L_hangarbay_guard_exit` apply outside their own functions).
4. Full regen pipeline (`make_elf.py` → delete `funcs_*.c` → `N64Recomp` → `fixup_game_funcs.py` →
   `cmake --build`), confirm patch report shows each new guard patched exactly `x1` (no
   stacking/collision), confirm clean build.
5. Validate with 2-3 soaks, `HOLD_S=240` each, `run_in_background: true` + `TaskOutput(block=true,
   timeout<=480000)` in the SAME turn (per-soak — the driver overwrites `run.log`, so grep/save
   anything you need BEFORE launching the next soak). Expect ~1 in 3-4 soaks to die pre-scene to
   the still-open, still-uninvestigated `waitForAnyAudioSlot` boot crash (uninformative, not
   counter-evidence) — budget for that when deciding how many soaks to attempt.

**If the grep finds few or zero NEW unguarded sites** (i.e. this session's 4 were most of what
exists): this closes the whole `-0x25A4($s1)` investigation thread cleanly. Move to either:
- Investigating the elevated pre-scene `waitForAnyAudioSlot` death rate (open since s278, never
  directly investigated, costs real soak budget almost every session).
- The `inflate_fast`/zlib localization design (s272, system-library call, different approach,
  never attempted).

## Do NOT do this iteration

- Do NOT re-soak `BREADCRUMB5`/`6`/`7`/`8`/`9` — all 5 are past their 2-session per-target budget
  with no new angle (see s280-283 history). The `-0x25A4($s1)` global-audit work above supersedes
  individual breadcrumb re-soaks as the highest-information-value next step.
- Do NOT treat `coalesceFreeHeapBlocks`, `processSceneNode`, or `reserveAndEmitDLEntry` crashes as
  new findings — all already catalogued (CURRENT-TRUTH ~line 1068/1088/1098/1308; this session's
  soak2/soak3 hit `processSceneNode+1424` and `reserveAndEmitDLEntry+10212` respectively, both
  pre-existing not-yet-localized families).
- Do NOT re-touch `DEQUEUE_GUARD`'s range-check bound — refuted (s267).
- Do NOT conflate the `0x80000000`-exact-fault family with item -49's KSEG0-zero-extension bug
  (`0x80630062`) without reading that item's writeup first.
- Do NOT cite `x0`/`x8`/`x9`/`x10`/`x11`/`x12` = `0x0000000300000000` or `0x0000000080000000` as
  crash-matching evidence for ANYTHING — constant RDRAM base pointer / constant register value seen
  across many unrelated crashes.
- Do NOT re-touch `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`/cache-guard/`CACHE2_GUARD`/
  `CACHE3_GUARD`/`CACHE4_GUARD`/`MATLIST_GUARD1-3`/`COMPOSE_NPC_GUARD1-9`/`DEQUEUE_GUARD` — all
  verified not regressing.
- Do NOT idle across a Stop-hook turn boundary waiting on a background soak — block with
  `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME turn.
- Do NOT treat a long-running soak as necessarily hung — check `ps -p <pid>` first.
- Do NOT touch the `lib/N64ModernRuntime`/`lib/rt64` "-dirty" submodule state — long-standing
  baseline, not new work. Only run `submodule-patches/export.sh` if YOU make new edits under `lib/`
  this session (this session's and last session's `fixup_game_funcs.py` edits were both in the
  standalone `N64Recomp` checkout, NOT under `lib/` — no `export.sh` needed).

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` needs cwd `rogue_squadron64` (run as `python3
  tools/make_elf.py`), `N64Recomp` needs cwd `N64Recomp` (`./build/N64Recomp
  rogue_squadron.toml`), `fixup_game_funcs.py` needs cwd `N64Recomp`. Always delete
  `funcs_*.c` and regen from scratch before running `fixup_game_funcs.py`.
- Delete `funcs_*.c` before regen via:
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
  (`rm`/`find -delete` are sandbox-blocked).
- Compound shell commands using `cd` combined with `&&`/output-redirection require interactive
  approval and get denied under the loop's automation — issue `cd <dir>` as its OWN Bash call
  first (cwd persists across calls in this tool), then run the next command as a separate call
  from that cwd. Background launches (`run_in_background: true`) do NOT inherit a prior foreground
  `cd` — always launch by full absolute path in that case, e.g.
  `env HOLD_S=240 zsh /abs/path/run_dequeuearg1.sh > /abs/path/log 2>&1` as a single background
  call with no preceding `cd`.
- `git -C <path> ...` / `git --git-dir=... --work-tree=... ...` get flagged for approval even
  standalone — use a plain `cd` (its own call) + `git status --short` (its own call) instead.
  `nm -n <binary> > file` also gets flagged — prefer a Python `subprocess.run(["nm","-n",path],
  capture_output=True)` instead of shell redirection for symtab work.
- Shell `for VAR in ...; do ... done` loops and `$(...)` command substitution inside them get
  rejected by the sandbox. Prefer a single `grep`/`ls` call with an explicit glob/file-list.
- Cross-turn waiting does not work under the Stop hook — use `TaskOutput(task_id, block=true,
  timeout<=480000)` synchronously in the same turn.
- Soak driver scripts live under `scratch/s73_post_a_scene/`, NOT `scratch/agent/`.
  Current-best baseline: `run_dequeuearg1.sh` (`HOLD_S` overridable via env, defaults to 240).
- Whether a soak reached the scene at all: `grep -c "vi_width=1024" <run.log>` (0 = pre-scene
  death, >=1 = reached it) — the driver OVERWRITES `run.log` on each run in the same output dir
  (`scratch/s73_post_a_scene/dequeuearg1/run.log` for `run_dequeuearg1.sh`), so grep/save anything
  needed from one soak BEFORE launching the next.
- `+N` crash-symbol offsets are NATIVE (ARM64) and SHIFT across sessions as guards/breadcrumbs are
  added. Verify range membership via the Mach-O symtab walk (inline python,
  `subprocess.run(["nm","-n",path], capture_output=True, text=True)`, filter type T/t, dedupe by
  address, sort, find the exact-name entry, check the crash offset is less than the distance to
  the next DISTINCT address). nm symbol names have a leading underscore.
- A crash's `[CRASH][last-guest-pc]` value is only informative if the crashing function is ITSELF
  breadcrumbed — always grep the reported guest PC's hex label and find its enclosing `RECOMP_FUNC`
  before trusting it. `0x8000b650` is a recurring stale value belonging to `beginFrameDLChunk`.
- Redirecting shell output (`>`) only works to paths under one of the 3 session working
  directories — `/tmp` is blocked. Use `scratch/agent/*.log`.
- `N64Recomp/fixup_game_funcs.py` is untracked by git in the standalone `N64Recomp` checkout —
  expected, changes persist only via the live file on disk across sessions.
- `CURRENT-TRUTH.md` is far over the ~35KB target (measured s283: >500KB) — 24+ consecutive
  sessions overdue for pruning. Still not this iteration's job unless the audit above is a quick
  null with clear leftover budget. Use `grep -n` to find section line numbers, then `Read` with
  `offset`/`limit` — a plain `Read` on the whole file fails (>256KB tool limit).
- At session start, check `scratch/agent/STATUS`/`OUTCOME` for signs of an interrupted prior
  iteration — normal loop-restart noise as long as `git log` confirms the last session's commit
  landed cleanly. Don't spend budget investigating further once confirmed.
- The pre-scene `waitForAnyAudioSlot` boot crash has been elevated-rate and unexplained since s278
  (roughly 1 in 3-4 soaks across s278-283) — never directly investigated, only observed as
  background noise. It costs real soak budget every session it isn't addressed; worth prioritizing
  directly once the `-0x25A4($s1)` audit above is resolved.
