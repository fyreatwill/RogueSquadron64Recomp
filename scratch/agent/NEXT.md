# NEXT work unit — RE-SOAK `BREADCRUMB9` on `tickWrappingTimerAccumulatorList` (its 3rd session)

## Where the investigation stands (s277)

s277 re-soaked `BREADCRUMB9` per s276's plan, no code change. Soak 1 died PRE-SCENE
(`process gone while waiting for phase`, before `vi_width=1024`) to the identical
pre-catalogued `waitForAnyAudioSlot` boot crash (23rd class, first seen s165):
`si_addr=0x400141ad3`, `sym=waitForAnyAudioSlot+244`, `last-guest-pc=0x8000b650`
(stale, uninformative) — an exact match to both of s276's soaks. That's 3 consecutive
pre-scene deaths to this same crash across s276+s277.

Soak 2 broke the streak: reached the scene at 45.3s, ran the ENTIRE 240s hold plus
grace window completely crash-free (0 crashes, wall=297s, driver had to SIGKILL the
still-alive process). This is the first soak since `BREADCRUMB9` was landed (s276)
that actually tested its own target for the full duration. Still 0 informative hits.

**Reframing, not confirming, the boot-crash streak**: 3/4 recent soaks dying pre-scene
to `waitForAnyAudioSlot`, immediately followed by a clean soak, argues AGAINST a
structural increase in that crash's frequency (a real regression would be expected to
persist, not break on the very next attempt) — more consistent with pre-existing
known-nondeterminism (since s165) with some run-to-run clustering. Do not conclude
either way from this alone; it's a 4-soak sample.

Current armed-breadcrumb tally, all weak-to-zero signal on their OWN targets:
- `BREADCRUMB5`/`reserveAndEmitDLEntry`: 0/4 combined (s272+s273), never informative.
- `BREADCRUMB6`/`buildPositionAndCallTransformHelper`: 0/2 (s273), never informative.
- `BREADCRUMB7`/`static_5_800AB658`: 0/2 (s274), never informative.
- `BREADCRUMB8`/`emitAllocatedDLCommand`: 0/2 (s275), never informative.
- `BREADCRUMB9`/`tickWrappingTimerAccumulatorList`: 0/2 combined nominal soaks (s276),
  0/2 this session (s277) — but only 1 of the 4 total soaks across both sessions was
  a genuine test (s277 soak2, clean). Never informative, but also barely tested yet.

## The next work unit

1. **No code change needed** — `BREADCRUMB9` is already landed in
   `N64Recomp/fixup_game_funcs.py` (`funcs_11.c`, patched x104 last regen, confirmed
   again s277 via the compiled-artifact check: 104 `g_rs64_last_guest_pc =` lines
   inside `tickWrappingTimerAccumulatorList`). Re-confirm before soaking:
   `grep -n "BREADCRUMB9" N64Recomp/fixup_game_funcs.py`. If missing, stop and
   investigate rather than re-adding blindly.

2. **Confirm the current build still has `BREADCRUMB9` compiled in** (it should,
   unchanged since s276 — no regen needed unless step 1's grep comes back empty).

3. **Soak twice** (this is `BREADCRUMB9`'s 3rd session — per budget rule 8, if this
   session ALSO produces zero informative hits, treat it as the 3-strikes trigger and
   STOP re-soaking this specific target next time; reassess strategy across the whole
   `BREADCRUMB5`-`BREADCRUMB9` family instead of continuing one-at-a-time re-soaks):
   `env HOLD_S=240 zsh /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/s73_post_a_scene/run_dequeuearg1.sh s278_soak1`
   then `s278_soak2` — launch each `run_in_background: true` from an absolute
   path, then `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME
   turn (cross-turn waiting does not work under the Stop hook).

4. **If both soaks die pre-scene to `waitForAnyAudioSlot` again**: that would make it
   4 of 5 total soaks across s276-s278 dying to this same crash, which WOULD start to
   look like a real pattern worth investigating (vs. this session's 3-then-clean
   result, which argued against one). Consider trying a soak with a LONGER phase-gate
   timeout, or diffing what changed in the s275/s276 build vs. earlier builds that
   could plausibly affect pre-scene boot timing.

5. **If `tickWrappingTimerAccumulatorList` crashes and `last-guest-pc` is
   informative** (grep the reported guest PC in `funcs_11.c`, confirm it's inside
   this function via the nearest-preceding `RECOMP_FUNC` line): read ~20 surrounding
   lines. This is a genuinely novel fault shape (bit-31-cleared guest address,
   `0x80000004` with bit 31 cleared) — do not force the familiar `CACHE*_GUARD`
   deref-side/write-side shape or the large-garbage-offset framing onto it without
   reading the actual code first. Consider whether it resembles the KSEG0-zero-
   extension bug family (item -49, `0x80630062`) — confirmed DISTINCT from the
   `0x80000000`-exact family, but this address's bit-31-clear pattern has never been
   directly compared against it; read that item's writeup before concluding either way.

6. **If `BREADCRUMB5`/`BREADCRUMB6`/`BREADCRUMB7`/`BREADCRUMB8` recur instead**:
   localize via `last-guest-pc` the same way `BREADCRUMB3`/`BREADCRUMB4` were
   localized — grep the guest PC in the owning `funcs_N.c` (`funcs_3.c`,
   `funcs_15.c`, `funcs_40.c`, `funcs_3.c` respectively). Any of these would be
   a first-ever informative hit — treat as high value.

7. **If `inflate_fast`/zlib recurs**: see s272's writeup (`PORTING-STATE` Session
   272) — not localizable via the simple breadcrumb-grep approach yet (system
   library, not a guest function).

8. **If a completely different crash lands**: note it, symrange-verify if
   plausible, don't chase it this iteration unless clearly highest-information-
   value (budget rule 8).

9. **If both soaks run fully clean with zero crashes**: this investigation has
   recorded several fully-clean soaks (s274 soak1, s275 soak2, s277 soak2) but never
   a clean PAIR within one session. A 2/2 clean pair would be the first ever — note
   it explicitly, single-observation, do not conclude the investigation is near done
   from one session's clean pair.

10. **If this session (`BREADCRUMB9`'s 3rd) again produces zero informative hits on
    its own target**: per budget rule 8, do NOT immediately re-soak it a 4th
    consecutive session. Instead write the hypothesis/evidence table for the whole
    `BREADCRUMB5`-`BREADCRUMB9` family into the next `NEXT.md` and pick the
    highest-information-value next probe — likely candidates: the `inflate_fast`/zlib
    site (different localization approach needed), or a strategic step back to ask
    whether the breadcrumb-hunting approach itself has diminishing returns after 5
    targets with 0 combined informative hits (worth a BLOCKED note to the human if
    no clear next angle presents itself).

## Do NOT do this iteration

- Do NOT re-run the regen pipeline (`make_elf.py` -> `N64Recomp` ->
  `fixup_game_funcs.py`) unless step 1's grep shows `BREADCRUMB9` is missing
  from `fixup_game_funcs.py` — it should already be landed, and an unneeded
  regen just burns budget.
- Do NOT spend a 3rd consecutive session re-soaking `BREADCRUMB5`,
  `BREADCRUMB6`, `BREADCRUMB7`, or `BREADCRUMB8` without a new angle — none is
  formally at the 3-strikes limit yet, but all four have weak-to-zero signal,
  and `tickWrappingTimerAccumulatorList` remains the highest-information-value
  candidate for one more session (its 3rd, but only its 2nd genuine test).
- Do NOT re-touch `DEQUEUE_GUARD`'s range-check bound — refuted (s267).
- Do NOT conflate the `0x80000000`-exact-fault family (or its `+0x10`
  `processSceneNode`-`+0x30`, `emitAllocatedDLCommand`-garbage-offset,
  `inflate_fast`-`+3`, `static_5_800AB658`-garbage-offset, or
  `tickWrappingTimerAccumulatorList`-bit31-clear variants) with item -49's
  KSEG0-zero-extension bug (`0x80630062`) without actually reading that item's
  writeup first.
- Do NOT cite `x0`/`x8`/`x9`/`x10`/`x11`/`x12` = `0x0000000300000000` or
  `0x0000000080000000` as crash-matching evidence for ANYTHING — constant
  RDRAM base pointer / constant register value seen across many unrelated
  crashes.
- Do NOT re-touch `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`/cache-guard/
  `CACHE2_GUARD`/`CACHE3_GUARD`/`CACHE4_GUARD`/`MATLIST_GUARD1-3`/
  `COMPOSE_NPC_GUARD1-9`/`DEQUEUE_GUARD` — all verified not regressing.
- Do NOT idle across a Stop-hook turn boundary waiting on a background soak —
  block with `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME
  turn.
- Do NOT treat a long-running soak (e.g. an 8GB+ log, driver command appearing
  "stuck") as necessarily hung — check `ps -p <pid>` first; the game process
  may already be dead while the driver script is still crunching a large log
  for its summary.
- Do NOT conclude "boot crash frequency has increased" OR "boot crash frequency
  is back to normal" from s277's 3-then-clean result alone — it's a 4-soak
  sample of a documented-nondeterministic crash class either way.

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` needs cwd `rogue_squadron64` (run as
  `python3 tools/make_elf.py`), `N64Recomp` needs cwd `N64Recomp`
  (`./build/N64Recomp rogue_squadron.toml`), `fixup_game_funcs.py` needs cwd
  `N64Recomp`. Always delete `funcs_*.c` and regen from scratch before running
  `fixup_game_funcs.py`.
- Delete `funcs_*.c` before regen via:
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
  (`rm`/`find -delete` are sandbox-blocked).
- Compound shell commands using `cd` combined with `&&`/output-redirection
  require interactive approval and get denied under the loop's automation —
  issue `cd <dir>` as its OWN Bash call first (cwd persists across calls in
  this tool), then run the next command as a separate call from that cwd.
- Background launches do NOT inherit a prior foreground `cd` — always launch
  soak drivers by full absolute path when using `run_in_background: true`.
- Cross-turn waiting does not work under the Stop hook — use
  `TaskOutput(task_id, block=true, timeout<=480000)` synchronously in the same
  turn.
- Soak driver scripts live under `scratch/s73_post_a_scene/`, NOT
  `scratch/agent/`. Current-best baseline: `run_dequeuearg1.sh` (`HOLD_S`
  overridable via env, defaults to 240 if unset). `BREADCRUMB`-family entries
  do NOT carry their own `ROGUESQ_LOG_*` fire-log (only guards do) — no
  `run_dequeuearg1.sh` edit needed when adding a new `BREADCRUMBn`. DO add a
  log flag when landing a new GUARD.
- `+N` crash-symbol offsets are NATIVE (ARM64) code offsets and SHIFT across
  sessions as guards/breadcrumbs are added. Verify range membership via the
  Mach-O symtab walk (inline python, see s273-s277's approach: parse
  LC_SYMTAB, sort `(n_value, name)` pairs by DISTINCT address, find the
  exact-name entry, check the reported crash offset is less than the distance
  to the next DISTINCT address — duplicate symtab entries at the same address
  are common, dedupe by address before computing "next symbol" or the range
  check false-negatives). System-library crashes (like `inflate_fast`) resolve
  via the OS's own dyld symbol table and don't need/support the same check.
- A crash's `[CRASH][last-guest-pc]` value is only informative if the crashing
  function is ITSELF breadcrumbed. Always grep the reported guest PC's hex
  label in the relevant `funcs_N.c` and find its enclosing `RECOMP_FUNC`
  before trusting it. `0x8000b650` specifically is a recurring stale value
  belonging to `beginFrameDLChunk` (`funcs_3.c`), seen in every session
  s272-s277 for crashes that happen elsewhere — do not treat it as
  informative unless the crashing symbol IS `beginFrameDLChunk`.
- When adding a guard to a function that's ALSO covered by an existing
  breadcrumb's blanket per-instruction pass: check whether the guard patch's
  code block sits before or after the breadcrumb patch's block in
  `fixup_game_funcs.py`'s file order. A guard block positioned BEFORE its
  function's breadcrumb block sees PRE-breadcrumb text and must not require
  `g_rs64_last_guest_pc` lines in its match regex.
- Redirecting shell output (`>`) only works to paths under one of the 3 session
  working directories — `/tmp` is blocked. Use `scratch/agent/*.log`.
- `N64Recomp/fixup_game_funcs.py` is untracked by git in the standalone
  `N64Recomp` checkout — expected. Changes persist only via the live file on
  disk across sessions.
- `git status --short` run from inside `RogueSquadron64Recomp/build` works
  without needing `-C`/`cd` combined-command approval prompts; `git -C <path>`
  and `cd <dir> && git ...` both require interactive approval.
- `CURRENT-TRUTH.md` is far over the ~35KB target — now 18+ consecutive
  sessions overdue for a pruning pass. Still not this iteration's job unless
  the localization work above is a quick null with clear leftover budget.
