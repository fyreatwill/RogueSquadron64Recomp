# NEXT work unit — test whether `BREADCRUMB9`'s instrumentation is a boot-crash confound

## Where the investigation stands (s278)

s278 re-soaked `BREADCRUMB9` per s277's plan (its 3rd session). No code change. BOTH soaks
died PRE-SCENE (`process gone while waiting for phase`, before `vi_width=1024`) to the
identical pre-catalogued `waitForAnyAudioSlot` boot crash (23rd class, first seen s165):
`si_addr=0x400141ad3`, `sym=waitForAnyAudioSlot+244`, `last-guest-pc=0x8000b650` (stale,
uninformative) — an exact match to s276/s277's deaths. The soak's own
`ROGUESQ_LOG_AUDIO_SLOT_ACTIVE_GUARD=1` fire-log recorded 0 hits in either soak (no positive
control from that angle, consistent with s166's original finding).

**0/2 this session, and this is `BREADCRUMB9`'s 3rd consecutive session with zero informative
hits on its own target — per ITERATION.md budget rule 8, this trips the 3-strikes threshold.**
Do NOT re-soak `BREADCRUMB9` again next session without a new angle.

**The actual finding this session**: a retrospective, no-soak-cost quantification across all
20 stored soak logs (`scratch/s73_post_a_scene/s27{0..8}_soak*/run.log`, classified by whether
each ever logged `vi_width=1024`) found:
- s270-s275 (6 sessions, 14 soaks): 3 pre-scene deaths / 14 = **21%**
- s276-s278 (3 sessions, 6 soaks): 5 pre-scene deaths / 6 = **83%**

This split lines up almost exactly with `BREADCRUMB9` landing at s276. It is consistent with —
but does NOT yet prove — the same "new instrumentation changes which bug wins a boot-time
race" confound this investigation has already documented twice (s93:
`ROGUESQ_LOG_THREAD_RESUME` silently changed which crash won a race; s160→s161:
rebuild-to-rebuild race-winner changes). This is a genuinely new, numbers-backed hypothesis —
stronger grounding than s277's "3-then-clean" read, which only had a 4-soak window and
explicitly declined to conclude either way.

Current armed-breadcrumb tally, all weak-to-zero signal on their OWN targets (unchanged, not
this session's focus):
- `BREADCRUMB5`/`reserveAndEmitDLEntry`: 0/4 combined (s272+s273), never informative.
- `BREADCRUMB6`/`buildPositionAndCallTransformHelper`: 0/2 (s273), never informative.
- `BREADCRUMB7`/`static_5_800AB658`: 0/2 (s274), never informative.
- `BREADCRUMB8`/`emitAllocatedDLCommand`: 0/2 (s275), never informative.
- `BREADCRUMB9`/`tickWrappingTimerAccumulatorList`: 0/2 combined genuine tests across 3
  sessions (6 soaks total, only 1 — s277 soak2 — a genuine full-duration test). 3-strikes hit.

## The next work unit

**Step 1 — free, no-soak check first (boring-first prior, do this before touching the build):**
Source-read the 4 call sites of `tickWrappingTimerAccumulatorList` to confirm/refute whether
any run during the pre-scene boot/menu phase (before the scene loads) — this is what would
make the instrumentation-confound hypothesis mechanically plausible at all:
```
grep -n "tickWrappingTimerAccumulatorList" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c
grep -n "tickWrappingTimerAccumulatorList" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_32.c
grep -n "tickWrappingTimerAccumulatorList" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_40.c
```
Call sites are at `funcs_27.c:108078`, `funcs_27.c:124149`, `funcs_32.c:2102`,
`funcs_40.c:5834` (found via grep in s278, not yet read). For each, read ~30 lines up to find
the enclosing `RECOMP_FUNC` and trace (via existing symbol-naming conventions / prior
PORTING-STATE entries) whether that enclosing function is part of the boot/menu/title-screen
path or only reachable once the scene is loaded. If none run pre-scene, the confound
hypothesis is refuted for free and you should skip straight to step 3 (the family reassessment)
rather than spending a soak on step 2.

**Step 2 — if step 1 finds a plausible pre-scene call site, run the discriminating soak:**
1. Comment out (do not delete) just the `BREADCRUMB9` block in
   `N64Recomp/fixup_game_funcs.py` — it's appended after the `BREADCRUMB8` block, patched x104
   last regen (`grep -n "BREADCRUMB9"` to find it exactly).
2. Regen: delete `funcs_*.c`
   (`python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`),
   `make_elf.py` (cwd `rogue_squadron64`) -> `N64Recomp` (cwd `N64Recomp`) ->
   `fixup_game_funcs.py` (cwd `N64Recomp`, save report, grep it — do NOT re-run the script) ->
   `cmake --build` (`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`). Confirm
   `BREADCRUMB9` did NOT patch (0 occurrences) and all other breadcrumbs/guards are unchanged
   at their documented counts (`BREADCRUMB5` x224, `BREADCRUMB6` x305, `BREADCRUMB7` x2643,
   `BREADCRUMB8` x222, `CACHE3_GUARD` x1, `CACHE4_GUARD` x1).
3. Soak twice, everything else unchanged:
   `env HOLD_S=240 zsh /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/s73_post_a_scene/run_dequeuearg1.sh s279_soak1`
   then `s279_soak2` — launch each `run_in_background: true` from an absolute path, then
   `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME turn (cross-turn waiting does
   not work under the Stop hook).
4. **Discriminating outcomes**: if both/most soaks now reach the scene (pre-scene rate reverts
   toward the ~21% baseline), that supports the instrumentation-confound hypothesis — treat
   `BREADCRUMB9` (or the breadcrumb mechanism's overhead in general) as a suspect worth a
   lighter-weight instrumentation approach. If pre-scene deaths persist at the ~83% rate even
   WITHOUT `BREADCRUMB9` compiled in, that refutes the confound — re-arm `BREADCRUMB9`
   afterward (uncomment, regen, rebuild) and fall back to step 3's family reassessment.
5. Re-arm `BREADCRUMB9` after this test regardless of outcome (uncomment the block, regen,
   rebuild) — its own hypothesis about crashes inside `tickWrappingTimerAccumulatorList` is
   still untested with only 1 genuine soak, just deprioritized below this confound check.

**Step 3 — if step 1 refutes the confound, or step 2 isn't reached this session — family
reassessment (do not skip this even if steps 1-2 consume the session):** write an explicit
hypothesis/evidence table for the whole `BREADCRUMB5`-`BREADCRUMB9` family (0 combined
informative hits across ~9 sessions) into the NEXT NEXT.md, and pick the highest-value probe
from the remaining backlog:
1. `inflate_fast`/zlib site (s272) — still only 1 observation, `si_addr=0x80000003`, needs a
   different localization approach (system library call, not a guest function — the breadcrumb
   mechanism doesn't apply directly).
2. Re-soak `BREADCRUMB5`/`BREADCRUMB6`/`BREADCRUMB7`/`BREADCRUMB8` once more each if nothing
   else looks better — none is at the 3-strikes limit yet, all have weak-to-zero signal
   (`BREADCRUMB5` 0/4 combined, `BREADCRUMB6` 0/2, `BREADCRUMB7` 0/2, `BREADCRUMB8` 0/2).
3. Consider a BLOCKED note to the human if no clear next angle presents itself — 5 targets
   with 0 combined informative hits is a real signal that the breadcrumb-hunting approach
   itself may have diminishing returns.

**If a genuinely new/different crash surfaces during any soak this session**: symrange-verify
if plausible (Mach-O symtab walk, see s273-s278's approach), don't chase it this iteration
unless clearly highest-information-value (budget rule 8) — note it for the backlog instead.

## Do NOT do this iteration

- Do NOT re-soak `BREADCRUMB9`'s own target a 4th consecutive session without a new angle —
  it hit the rule-8 3-strikes threshold this session (s278). The confound test in step 2 is a
  DIFFERENT hypothesis (about instrumentation overhead, not about the target function itself),
  so it doesn't count as a 4th strike on the same sub-hypothesis — but don't use that as a
  loophole to just re-soak with `BREADCRUMB9` still armed and call it something new.
- Do NOT skip step 1 (the free source-read) and jump straight to a soak — if the 4 call sites
  turn out to be scene-only (not boot/menu), the whole confound hypothesis is mechanically
  impossible and a soak would be wasted budget.
- Do NOT conclude the instrumentation-confound hypothesis is CONFIRMED from a single soak
  pair even if step 2 supports it — this needs the two-source rule (one soak pair reverting
  toward baseline is suggestive, not proof; consider a 2nd confirming pair before writing it
  into CURRENT-TRUTH as settled).
- Do NOT leave `BREADCRUMB9` permanently disabled if step 2 runs — re-arm it afterward
  (uncomment, regen, rebuild) regardless of the outcome, per step 5.
- Do NOT spend a 3rd consecutive session re-soaking `BREADCRUMB5`, `BREADCRUMB6`,
  `BREADCRUMB7`, or `BREADCRUMB8` without a new angle — none is formally at the 3-strikes
  limit yet, but all four have weak-to-zero signal.
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
  separate call from that cwd.
- Shell `for VAR in ...; do ... done` loops and `$(...)` command substitution inside them get
  rejected by the sandbox ("Contains simple_expansion") even when individually each piece
  would be fine — observed s278. Prefer a single `grep`/`ls` call with an explicit glob or
  explicit file-list argument (grep accepts multiple files and reports per-file with `-c`/`-l`)
  over a shell loop when scanning multiple files. If Python is needed, avoid reading huge
  (multi-GB) log files fully into memory — use `grep -c`/`grep -l` for classification instead of
  `open().read()`, which can time out (observed s278, a 20-file full-read job hit the 120s
  timeout while `grep` on the same files was near-instant).
- Background launches do NOT inherit a prior foreground `cd` — always launch soak drivers by
  full absolute path when using `run_in_background: true`.
- Cross-turn waiting does not work under the Stop hook — use `TaskOutput(task_id, block=true,
  timeout<=480000)` synchronously in the same turn.
- Soak driver scripts live under `scratch/s73_post_a_scene/`, NOT `scratch/agent/`.
  Current-best baseline: `run_dequeuearg1.sh` (`HOLD_S` overridable via env, defaults to 240 if
  unset). `BREADCRUMB`-family entries do NOT carry their own `ROGUESQ_LOG_*` fire-log (only
  guards do) — no `run_dequeuearg1.sh` edit needed when adding a new `BREADCRUMBn`. DO add a
  log flag when landing a new GUARD.
- Whether a soak reached the scene at all can be checked cheaply via `grep -c "vi_width=1024"
  <run.log>` (0 = pre-scene death, >=1 = reached it) — cheaper than relying on the driver's own
  stdout message (`process gone while waiting for phase`), which is NOT written into `run.log`
  itself (only to the driver's own terminal output, which isn't persisted after the task
  completes) — observed s278, `grep` on that phrase against `run.log` returns 0 hits even for
  known pre-scene deaths.
- `+N` crash-symbol offsets are NATIVE (ARM64) code offsets and SHIFT across sessions as
  guards/breadcrumbs are added. Verify range membership via the Mach-O symtab walk (inline
  python, see s273-s278's approach: parse LC_SYMTAB, sort `(n_value, name)` pairs by DISTINCT
  address, find the exact-name entry, check the reported crash offset is less than the
  distance to the next DISTINCT address — duplicate symtab entries at the same address are
  common, dedupe by address before computing "next symbol" or the range check
  false-negatives). System-library crashes (like `inflate_fast`) resolve via the OS's own dyld
  symbol table and don't need/support the same check.
- A crash's `[CRASH][last-guest-pc]` value is only informative if the crashing function is
  ITSELF breadcrumbed. Always grep the reported guest PC's hex label in the relevant
  `funcs_N.c` and find its enclosing `RECOMP_FUNC` before trusting it. `0x8000b650`
  specifically is a recurring stale value belonging to `beginFrameDLChunk` (`funcs_3.c`), seen
  in every session s272-s278 for crashes that happen elsewhere — do not treat it as
  informative unless the crashing symbol IS `beginFrameDLChunk`.
- When adding a guard to a function that's ALSO covered by an existing breadcrumb's blanket
  per-instruction pass: check whether the guard patch's code block sits before or after the
  breadcrumb patch's block in `fixup_game_funcs.py`'s file order. A guard block positioned
  BEFORE its function's breadcrumb block sees PRE-breadcrumb text and must not require
  `g_rs64_last_guest_pc` lines in its match regex.
- Redirecting shell output (`>`) only works to paths under one of the 3 session working
  directories — `/tmp` is blocked. Use `scratch/agent/*.log`.
- `N64Recomp/fixup_game_funcs.py` is untracked by git in the standalone `N64Recomp` checkout —
  expected. Changes persist only via the live file on disk across sessions.
- `git status --short` run from inside `RogueSquadron64Recomp/build` works without needing
  `-C`/`cd` combined-command approval prompts; `git -C <path>` and `cd <dir> && git ...` both
  require interactive approval.
- `CURRENT-TRUTH.md` is far over the ~35KB target (measured s278: 493KB, ~14x over) — now 19+
  consecutive sessions overdue for a pruning pass. Still not this iteration's job unless the
  localization work above is a quick null with clear leftover budget.
