# NEXT work unit — land `BREADCRUMB5` scoped to `reserveAndEmitDLEntry` (the
# newest, best-evidenced not-yet-localized crash site), regen, re-soak to
# localize it exactly; if `processSceneNode+1184`/`BREADCRUMB4` or the other
# new site (`emitAllocatedDLCommand`) recurs instead, localize/guard that one
# instead per the existing playbook.

## Where the investigation stands (s271)

s271 ran s270's plan exactly: re-soaked twice with the build as-is
(`BREADCRUMB4` armed, `CACHE3_GUARD` landed, no code changes first).

**`processSceneNode+1184` did NOT recur in either soak** (0/2 this session,
now 0/4 combined across s270+s271 — down from 3/5 after s267+s269+s270).
`BREADCRUMB4` stays armed and unconsumed. Stop citing the old "3/3, most
reproducible" framing from s269 — it was based on too few data points and has
since been revised down twice.

**Soak 1** caught a brand-new, symrange-confirmed crash: `emitAllocatedDLCommand+6608`,
`si_addr` = RDRAM base + `0xd2095209` (a garbage/corrupted offset, NOT the
`0x80000000`-exact family this investigation has mostly been tracking) —
single observation, different fault shape, not yet localized.

**Soak 2 finally caught and exactly localized `BREADCRUMB3`'s own long-elusive
target**: `beginFrameDLChunk+21216`, `si_addr=0x380000000` exactly (guest
`0x80000000`). Because `beginFrameDLChunk` is itself breadcrumbed,
`last-guest-pc=0x8000b03c` was informative for the first time on this family
and pinpointed `funcs_3.c`'s `0x8000B03C: lw $v0, 0x0($v0)` — a 4th unguarded
copy of the "reload persistent free-list cache-head global (`0x801163B0`),
deref with zero validation" idiom (3 prior copies, all in
`submitSceneNodeRender`, fixed s197/s266/s270). Landed and soak-verified
`CACHE4_GUARD` (2/2 valid runs, 0/2 recurrence of this specific crash —
**note: neither verify run's fire-log ever triggered, so this is
code-reading-justified, not fire-confirmed**; same caveat level s270 accepted
for `CACHE3_GUARD`).

**`verify2` (guard-verification soak 2) surfaced a 5th, not-yet-guarded copy**
of the exact same idiom: `reserveAndEmitDLEntry+7160`, `si_addr=0x380000000`
exactly, symrange-confirmed in-range. Single observation, not yet localized
beyond nearest-symbol (not breadcrumbed, `last-guest-pc` uninformative for
it). This is now the best-evidenced next target: same fault family as 4
already-confirmed/fixed sites, strong prior that it's a 6th call site of the
same idiom.

`ROGUESQ_LOG_SCENE_NODE_CACHE3_GUARD` and `ROGUESQ_LOG_SCENE_NODE_CACHE4_GUARD`
were missing from `run_dequeuearg1.sh` (only `CACHE_GUARD`/`CACHE2_GUARD` were
exported) — added both this session. Future guards should get their log flag
added to the driver script in the SAME session they're landed, not left for a
future session to notice missing.

## The next work unit

1. **Land `BREADCRUMB5` scoped to `reserveAndEmitDLEntry`'s own body** — same
   mechanism as `BREADCRUMB`-`BREADCRUMB4` (shared `g_rs64_last_guest_pc`
   global, no `main.cpp` change). First confirm which `funcs_N.c` file it's
   in: `grep -n "RECOMP_FUNC void reserveAndEmitDLEntry" N64Recomp/RecompiledFuncs/funcs_*.c`.
   **Check the ordering gotcha before writing any guard-adjacent code**: if
   you land both the breadcrumb AND a guard for this function in the same
   session, and the guard patch's block sits BEFORE the breadcrumb patch's
   block in `fixup_game_funcs.py`'s file order, the guard's regex must NOT
   include `g_rs64_last_guest_pc` lines (see s271's `CACHE4_GUARD` writeup in
   `PORTING-STATE.md` Session 271 for the exact reasoning and a worked
   example) — or place the guard's code block AFTER the breadcrumb's block
   instead, matching the post-breadcrumb text, whichever is less error-prone
   given the actual file layout at the time.

2. **Full regen** (delete `funcs_*.c` first — see iron rule below), build,
   then re-soak: `env HOLD_S=240 zsh scratch/s73_post_a_scene/run_dequeuearg1.sh <tag>`
   (launch `run_in_background: true` from an absolute path, then immediately
   `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME turn).
   Budget 2 attempts before deciding what to do with the result (iron rule 8).

3. **If `reserveAndEmitDLEntry` crashes and `last-guest-pc` is now
   informative** (function is breadcrumbed): `grep -n
   "0x<UPPERCASE_HEX>:"` in whichever `funcs_N.c` file around the reported
   guest PC, read ~20 surrounding lines. If it matches the cached-free-list-head
   idiom shape (`lui $vX,0x8011` / `lw $vX,0x63B0($vX)` / deref or +4-store
   with zero validation), add `CACHE5_GUARD` — same shape as `CACHE4_GUARD`
   if it's a deref-side crash, or `CACHE2_GUARD`/`CACHE3_GUARD` if it's a
   write-side (`sw $zero, 0x4($v0)`) crash — full regen, soak-verify (≥2
   independent clean runs, iron rule 4), and this time make sure to add the
   guard's `ROGUESQ_LOG_*` flag to `run_dequeuearg1.sh` in the SAME session.

4. **If `processSceneNode+1184` (`BREADCRUMB4`'s target) recurs instead**:
   localize via `last-guest-pc` (now genuinely informative since
   `processSceneNode` is breadcrumbed) the same way s271 localized
   `beginFrameDLChunk`'s crash — grep the reported guest PC in `funcs_4.c`,
   add ONE targeted guard matching whatever idiom is found, regen,
   soak-verify.

5. **If `emitAllocatedDLCommand` crashes again**: this is a DIFFERENT fault
   shape (`si_addr` was a garbage offset, not exactly `0x80000000`) — don't
   assume it's the same idiom family. Land a breadcrumb on it first if it
   recurs, to get an informative `last-guest-pc` before guessing at a fix.

6. **If a completely different crash lands** (has happened most sessions):
   note it, symrange-verify if the offset looks plausible, but don't chase it
   this iteration unless it's clearly the highest-information-value next
   step — see iron rule 8's budget discipline.

## Do NOT do this iteration

- Do NOT run `fixup_game_funcs.py` twice in a row without deleting and
  regenerating `funcs_*.c` in between — this SILENTLY DUPLICATES every
  breadcrumb insertion. Always: delete `funcs_*.c` -> `make_elf.py` ->
  `N64Recomp` -> `fixup_game_funcs.py` ONCE -> check multiplicities -> build.
- Do NOT spend another soak attempt on `heapFreeListDequeue`'s own
  BREADCRUMB2-targeted crash — it's 0/6 across 2 sessions, parked per rule 8.
- Do NOT re-touch `DEQUEUE_GUARD`'s range-check bound — the a0-argument
  hypothesis is refuted (s267) with a same-run positive control.
- Do NOT conflate the `0x80000000`-exact-fault family (or its `+0x30`
  variant at `processSceneNode`, or `emitAllocatedDLCommand`'s
  garbage-offset variant — that one is NOT confirmed same-family) with
  item -49's KSEG0-zero-extension bug (`0x80630062`) — different exact
  values, different sites, confirmed distinct multiple sessions running.
- Do NOT cite `x0`/`x8`/`x9`/`x10`/`x11` = `0x0000000300000000` as
  crash-matching evidence for ANYTHING — constant RDRAM base pointer (s219,
  item -60).
- Do NOT re-touch `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`/cache-guard/
  `CACHE2_GUARD`/`CACHE3_GUARD`/`CACHE4_GUARD`/`MATLIST_GUARD1-3`/
  `COMPOSE_NPC_GUARD1-9`/`DEQUEUE_GUARD` — all verified not regressing and
  not the current blocker.
- Do NOT treat `emitAllocatedDLCommand`'s crash as confirmed-related to the
  `0x80000000` family — its `si_addr` was a different, garbage offset, not
  exactly `0x80000000`. Single observation, unlocalized.
- Do NOT claim `CACHE4_GUARD` is fire-confirmed — both verification soaks
  showed zero recurrence of the target crash AND zero fire-log lines. It is
  accepted on code-reading + no-regression grounds only, same bar s270 used
  for `CACHE3_GUARD`. If a future soak's log ever shows
  `[scene-node-cache4-guard]` firing, that upgrades this to a confirmed fix
  and is worth noting explicitly.
- Do NOT idle across a Stop-hook turn boundary waiting on a background
  soak — block with `TaskOutput(task_id, block=true, timeout<=480000)` in
  the SAME turn.

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` needs cwd `rogue_squadron64` (run as
  `python3 tools/make_elf.py`), `N64Recomp` needs cwd `N64Recomp`
  (`./build/N64Recomp rogue_squadron.toml`), `fixup_game_funcs.py` needs cwd
  `N64Recomp`. Always delete `funcs_*.c` and regen from scratch before
  running `fixup_game_funcs.py` — see the duplication warning above.
- Delete `funcs_*.c` before regen via:
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
  (`rm`/`find -delete` are sandbox-blocked).
- Background launches do NOT inherit a prior foreground `cd` — always
  launch soak drivers by full absolute path when using
  `run_in_background: true`. Likewise, foreground `Bash` calls that use
  relative paths can transiently fail right after a background soak launch
  writes new files (observed s271, resolved on retry with an absolute
  path) — prefer absolute paths for any file check immediately after a
  soak completes.
- Cross-turn waiting does not work under the Stop hook — use
  `TaskOutput(task_id, block=true, timeout<=480000)` synchronously in the
  same turn.
- Soak driver scripts live under `scratch/s73_post_a_scene/`, NOT
  `scratch/agent/`. Current-best baseline: `run_dequeuearg1.sh` (`HOLD_S`
  overridable via env, defaults to 240 if unset). It now exports
  `ROGUESQ_LOG_SCENE_NODE_CACHE_GUARD` through `CACHE4_GUARD` — when landing
  a new guard, add its log flag to this script in the SAME session, or a
  future session will get an uninformative "0 fires" verification run like
  s271 did for `CACHE4_GUARD`'s first verify attempt.
- `+N` crash-symbol offsets are NATIVE (ARM64) code offsets and SHIFT across
  sessions as guards/breadcrumbs are added (confirmed s271:
  `beginFrameDLChunk`'s guest-`0x80000000` crash moved from native `+13420`
  at s268 to `+21216` at s271, same guest-side signature). Don't assume a
  changed native offset means a different bug — check `si_addr`/guest PC
  first. Verify range membership by reading `build/RogueSquadron64Recomp`'s
  Mach-O symtab directly — see `scratch/agent/s268_symrange2.py` for the
  reusable parser/walker (edit its `targets` list or copy the walk logic
  inline); run it with cwd `RogueSquadron64Recomp/build` so the relative
  binary path resolves. No `nm`/`atos`/`otool`/`lldb`/`dwarfdump` needed or
  available.
- A crash's `[CRASH][last-guest-pc]` value is only informative if the
  crashing function is ITSELF breadcrumbed — otherwise it just shows
  wherever the process last passed through one of the OTHER currently-
  instrumented functions (stale, confirmed misleading multiple times this
  investigation, but ALSO confirmed genuinely informative when the crash
  IS in a breadcrumbed function — s271's `beginFrameDLChunk` localization).
  Check which file/function the crash symbol is in before trusting
  `last-guest-pc` for it.
- When adding a guard to a function that's ALSO covered by an existing
  breadcrumb's blanket per-instruction pass: check whether your guard
  patch's code block sits before or after the breadcrumb patch's block in
  `fixup_game_funcs.py`'s file order. Patches apply sequentially against one
  shared `text` variable — a guard block positioned BEFORE its function's
  breadcrumb block sees PRE-breadcrumb text and must not require
  `g_rs64_last_guest_pc` lines in its match regex (s271, `CACHE4_GUARD`).
- Redirecting shell output (`>`) only works to paths under one of the 3
  session working directories (`RogueSquadron64Recomp`, `N64Recomp`,
  `rogue_squadron64`) — `/tmp` is blocked. Use `scratch/agent/*.log`.
- `N64Recomp/fixup_game_funcs.py` is untracked by git in the standalone
  `N64Recomp` checkout — expected, not a bug; not a `lib/` submodule so
  `submodule-patches/export.sh` never applies to it. Its changes persist
  only via the live file on disk across sessions. Same is true of
  `scratch/` in general (`RogueSquadron64Recomp/.gitignore` excludes
  `/scratch/` wholesale) EXCEPT `scratch/agent/NEXT.md`, `STATUS`, and
  `OUTCOME`, which are individually force-tracked — everything else under
  `scratch/` (including soak driver scripts like `run_dequeuearg1.sh`)
  persists only via the live file on disk, never via git.
- `git status --short` run from inside `RogueSquadron64Recomp/build` (or any
  subdir) works without needing `-C`/`cd` combined-command approval prompts;
  `git -C <path>` and `cd <dir> && git ...` both require interactive
  approval in this environment and may not resolve non-interactively.
- `CURRENT-TRUTH.md` is far over the ~35KB target in CLAUDE.md (now ~7000
  lines / several hundred KB — the file exceeds the Read tool's 256KB limit
  in one shot, requiring offset/limit reads). A dedicated pruning session is
  now 13+ consecutive sessions overdue — still not this iteration's job
  unless the localization work above is a quick null with clear leftover
  budget.
