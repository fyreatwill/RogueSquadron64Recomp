# NEXT work unit — `hangarInitialize` chunk 2 (lines 124187-124999)
# continuing the chunked `-0x25A4($s1)` audit from s285

## Where the investigation stands (s285)

s285 completed `hangarInitialize` chunk-1 (`funcs_27.c` lines 119804-124186, the function's true
first epilogue) — picked up from an interrupted prior session that had already done the
classification and guard-landing but never validated or committed. Full detail: `PORTING-STATE`
Session 285, `CURRENT-TRUTH` item -126.

**What happened**: verified the interrupted session's classification via a dedicated
reconciliation pass (38 raw hits = 1 write + 11 safe + 26 guarded, all accounted for — the
original summary's "9 safe" was undercounted by 2, a documentation slip not a coverage gap).
Validation soak2 crashed inside `static_5_800A9270` (a function s283/s284 believed "fully
guarded, 4/4") at a NEW site — direct source re-read found a genuine unguarded dereference (guest
`0x800A92FC`, the existing `HANGARLIST_GUARD` checks the dereference's result, not the pointer
that produced it). Fixed as `S285_A9270_R4`. 2 more soaks (2 informative, scene-reaching) did not
reproduce it or fire the new guard.

**Confirmed function structure** (from a direct `return;` grep, not estimated): `hangarInitialize`
spans `funcs_27.c` lines 119804-133573, with exactly 4 `return;` epilogues inside it, at lines
**124187** (chunk-1's end, done), **124999**, **125808**, **132609** — plus the function's own
final close at 133573. This gives 4 remaining chunks:
- Chunk 2: 124187-124999 (~800 lines) — **this session's target**
- Chunk 3: 124999-125808 (~800 lines)
- Chunk 4: 125808-132609 (~6800 lines, by far the largest — will need its own sub-chunking)
- Chunk 5: 132609-133573 (~1000 lines)

Do NOT reuse the old estimates from s284 (`~123792, ~124604, ~125413, ~132214, ~133175`) — they
were off by 300-800 lines each; the boundaries above are grep-verified against the actual file.

**Also confirmed**: immediately after the chunk-1 epilogue (`after_80:` / line ~124160-124187),
the disassembly contains an inline-duplicated copy of `static_5_800AAD9C`'s own body (guest
`0x800AAD9C` follows contiguously after `hangarInitialize`'s `jr $ra` at `0x800AAD98` in the
original ROM). `static_5_800AAD9C` is a SEPARATE function (`funcs_40.c:5530`), already fully
guarded (2/2, s284). **When you grep chunk 2 for `-0X25A4` hits, do NOT re-classify anything that
is actually this inline-duplicated `static_5_800AAD9C` body** — cross-check any hit near the
chunk-2 start against `static_5_800AAD9C`'s own guest-address range (roughly `0x800AAD9C` onward)
before treating it as new `hangarInitialize` surface. If chunk 2's start (guest-address-wise)
overlaps this duplicated region, skip it (it's already covered by `static_5_800AAD9C`'s own
guards) and start real classification wherever `hangarInitialize`'s own unique code resumes.

## The next work unit

**Classify and guard chunk 2: lines 124187-124999 of `funcs_27.c`.**

1. Get the exact `-0X25A4` hit line numbers in this chunk:
   `grep -n "0X25A4" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c`
   filtered to `$1>=124187 && $1<=124999`. Count them exactly — do not assume a proportional
   share of the function's 103 total hits; chunk 1 alone (only ~30% of the function's line count)
   held 38 of the ~110+ actual hits once inline-duplication and the corrected boundary are
   accounted for, so hit density is NOT uniform across the function.
2. Before delegating classification, check whether any of this chunk's start overlaps the
   inline-duplicated `static_5_800AAD9C` body described above (read the first ~50 lines of the
   chunk and check the guest addresses in the `//0x...` comments against `0x800AAD9C`+; if they're
   still below `0x800AAD9C`, you're still in the duplicate region — skip forward to where
   `hangarInitialize`'s own unique code resumes, likely marked by a new distinct guest address
   range not matching `static_5_800AAD9C`'s or `static_5_800AB1C8`'s known ranges).
3. Delegate classification to a background/foreground agent: give it the file, the line range, the
   exact hit line numbers, the GUARDED/UNGUARDED-DEREF/SAFE criteria, and explicitly require it to
   check the **third-hop-capable pattern found 3 times now** (s282 `G32`, s284 `SECONDHOP`, s285
   `R4`): for every `-0x25A4` reload, trace whether the IMMEDIATELY-COMPUTED address from that
   reload is dereferenced before its OWN check — do not accept "a later guard checks a value
   loaded further downstream" as sufficient coverage for an earlier, unchecked dereference in the
   same chain.
4. After classification, get an INDEPENDENT reconciliation pass (a second agent or your own
   direct check) confirming raw-hit-count == (write + safe + guarded), the same check that caught
   the interrupted session's 2-site undercount in chunk 1. Do not skip this — it already found a
   real (small) discrepancy once.
5. Verify anchor-pattern uniqueness within `funcs_27.c` (`text.count(anchor) == 1`) BEFORE
   splicing into `fixup_game_funcs.py`.
6. Batch every genuinely unguarded site in this chunk into one fixup-script edit.
7. Regen: delete `funcs_*.c`, run `N64Recomp`, run `fixup_game_funcs.py` **exactly once** (s285's
   own mistake this session: re-ran fixup on an already-patched file and stacked a duplicate guard
   — caught before building via an anchor-count check, but avoid repeating it — always regenerate
   fresh from `N64Recomp` between any two fixup runs, never run fixup twice in a row).
8. Build, then validate with 2-3 soaks (`HOLD_S=240`, `run_in_background: true` +
   `TaskOutput(block=true, timeout<=480000)` in the same turn). If a soak's wrapper script hangs in
   its post-hold summary/screenshot phase (seen once this session, ~15 min hang spawning repeated
   `run_mission_keys.sh`, unrelated to game state — the raw `run.log` already had the complete
   answer with no further activity), check `run.log` directly for `[CRASH][pc-symbol]` and
   `vi_width=1024` rather than waiting indefinitely on the wrapper; SIGKILL the stuck wrapper tree
   once the raw log confirms the outcome.

## Do NOT do this iteration

- Do NOT attempt chunk 3, 4, or 5 — one chunk per session, per the established rule.
- Do NOT re-touch `static_5_800AAD9C`, `static_5_800AB1C8`, `static_5_800ADB70`, `static_5_800AB658`
  (`G1`-`G32`/`BREADCRUMB5`-`9`), or chunk-1's `S285_H1_*` guards — all validated this session or
  earlier.
- Do NOT assume `static_5_800A9270` is now fully closed just because `R4` is fixed — it has missed
  sites twice (s284, s285); if it crashes again, treat it as informative, not noise.
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
- `git -C`/`git --git-dir=` get flagged even standalone — use plain `cd` + `git status --short` as
  separate calls. `nm -n <binary> > file` also flagged — use Python `subprocess.run`.
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
- `CURRENT-TRUTH.md` is far over the ~35KB target (26+ sessions overdue) — not this iteration's
  job unless the chunk-2 audit is a quick null with clear leftover budget.
- At session start, check `scratch/agent/STATUS`/`OUTCOME` for signs of an interrupted prior
  iteration — this session (s285) found real, valuable half-finished work this way (an entire
  chunk-1 classification+guard+partial-soak already done in `fixup_game_funcs.py` and
  `scratch/agent/s285_sites.py`/`s285_verify.py`). Always check whether uncommitted work already
  exists in `N64Recomp/fixup_game_funcs.py` (diff against what `PORTING-STATE`'s last committed
  session describes) before starting fresh classification from scratch.
- The pre-scene `waitForAnyAudioSlot` boot crash remains elevated-rate and unexplained since s278
  — still never directly investigated, only observed as background noise.
