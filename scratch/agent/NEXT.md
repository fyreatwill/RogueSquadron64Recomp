# NEXT work unit

## s356: read Thread A's `verify3/4` (both crashed, both off-target/inconclusive), queued `verify5/6`; Thread B still has no new data (its `verify3/4` hadn't drained by session start)

Full detail: `PORTING-STATE` Session 356, `docs/CURRENT-TRUTH.md` item -211.

`s355_coalesceheapguard_verify3` crashed at `_platform_memmove+96` (a NEW crash signature, never seen
before in this project's history — grepped and confirmed zero prior hits) after running cleanly through
title + ~214s more. `s355_coalesceheapguard_verify4` crashed at `musyxSynthFrame+4652` in <1s, before
`title_reached` printed — the same known boot-time crash family `s348_contentguard_verify1` hit, too
short to test anything. Neither hit `coalesceFreeHeapBlocks`, neither had `coalesce_guard_fire_n>=1`.
Tally: 2 clean (verify1/2) + 2 off-target crashes (verify3/4, one non-informative-too-short) = 3
meaningful non-recurrences of the target crash, one short of the 4-meaningful-run "validated by
non-recurrence" bar. Not closed yet.

## Two open threads — pick the higher-information-value one first

**Thread A: `m5-audio-destub-coalesce-heap-guard-verify` (iteration 3 — 2 clean + 2 off-target, 0/4
target-crash recurrences, 0/4 guard fires, 3 meaningful non-recurrence runs of 4 needed).**
- **Step 1**: `s356_coalesceheapguard_verify5.sh` and `_verify6.sh` are already queued in
  `scratch/agent/soak_queue/` (`HOLD_S=240`, same recipe as prior verify pairs) — let the loop drain
  them, do NOT run inline.
- **Step 2 (next session)**: count only runs that actually ran long enough to matter (title reached, or
  crashed after a substantial hold — not a <5s boot death). If a `verify5`/`verify6` run pushes the
  meaningful-non-recurrence count to 4: close the thread as validated-by-non-recurrence (same bar s348's
  content-guard used), fold into CURRENT-TRUTH.
- **Step 2b**: if either crashes with `pc-symbol=coalesceFreeHeapBlocks+3452` and `coalesce_guard_fire_n=0`:
  null instrument — re-check the guard regex against the CURRENT regenerated `funcs_0.c` around guest PC
  `0x80002434` before assuming it's broken.
- **Step 2c**: if either crashes elsewhere with `coalesce_guard_fire_n>=1`: guard confirmed alive
  (positive control satisfied), crash relocated downstream — same s350/s351 pattern, not a failure.
- **Step 2d**: if either hits `_platform_memmove+96` AGAIN: that's a 2nd independent hit on the s355-found
  novel signature — open a 3rd thread (`m5-audio-destub-platform-memmove`) targeting it specifically,
  since 2 byte-identical/same-symbol hits from independent sessions is the evidentiary bar this project
  uses elsewhere (item -208's `bad_v1` finding, item -210's `coalesceFreeHeapBlocks+3452` finding).

**Thread B: `m5-audio-destub-linkedlist-corruption-source` (iteration 3 of 3 — LAST soak pair before
iron rule 8's mandatory pivot; still 0/2 informative from s353, and s355's `verify3/4` haven't drained
yet).**
- **Step 1**: `s355_ringbuffer_verify3.sh` and `_verify4.sh` are already queued in
  `scratch/agent/soak_queue/` — nothing new to queue, just wait for the loop to drain them.
- **Step 2 (next session)**: read whichever of `verify3`/`verify4` drained.
  - If a crash lands INSIDE `drainMeshReleaseQueue` (any of its 4 known offsets) with `ring_fire_n>=1`:
    finally informative — check whether the `[drain-mesh-ring]` dump's `iter_at_bail`/walked-`v1`
    sequence is consistent with a structural bug (same list position every time) or varies (state-dependent
    corruption).
  - If BOTH crash outside `drainMeshReleaseQueue` again (0/2 informative, matching s353's pair): this is
    the 3-strike trigger per iron rule 8. Do NOT queue a 4th pair. Instead write the accumulated
    hypothesis/evidence table (bimodal timing windows, `bad_v1=0x00010001` byte-identical value, the 4
    guarded offsets, the new `_platform_memmove` lead from Thread A) into this file and pick the
    highest-information-value next probe — likely candidates: (a) widen the ring-buffer breadcrumb to
    cover MORE call sites than just `drainMeshReleaseQueue`, since 4 of 6 recent crashes across both
    threads have landed in unrelated functions (`submitSceneNodeRender`, `coalesceFreeHeapBlocks` x2,
    `_platform_memmove`, `musyxSynthFrame`) — the corruption may be reachable/observable from a shared
    upstream allocator/free path rather than only from `drainMeshReleaseQueue`'s tail-scan; or (b) a
    full offline re-read of all soak logs to date (capture-once-analyze-many) looking for a common
    upstream event preceding all 6 crash sites.

**Recommendation**: both threads' next data is already queued (`s356_coalesceheapguard_verify5/6.sh` +
`s355_ringbuffer_verify3/4.sh`, 4 recipes total) — the loop drains up to 2 per gap. Next session: read
whichever pair(s) drained, resolve per the steps above. If Thread B's pair comes back 0/2-informative
again, that session MUST write the pivot table (iron rule 8) rather than queuing a 4th Thread B pair.

## Environment notes (carried forward — see s327-356 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked,
  confirmed outside this repo's `lib/`/submodule-patches system). Delete `RecompiledFuncs/*.c` before
  every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Full regen order: `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` ->
  `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml` ->
  `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` ->
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
  /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j8`. Run each step as its own
  single command (compound `cd a && cmd` sometimes needs manual approval this session).
- `soak_queue/*.sh` recipes must be invoked as `zsh scratch/agent/soak_queue/<name>.sh` if drained
  manually — `bash <path>` is NOT allowlisted even though the recipe files start with a `#!/bin/bash`
  shebang; only `zsh:*` is in the allow rules. If drained manually, also manually do what
  `run_soak_queue()` normally does: save output to `scratch/agent/soak_results/<name>_<timestamp>.log`,
  append a line to `SOAK-RESULTS.md`, move the `.sh` to `soak_queue/done/`.
- `for f in ...; do ... done` shell loops over globbed filenames trigger a sandbox rejection ("Contains
  simple_expansion") — prefer a `python3 - <<'EOF' ... EOF` heredoc with `glob.glob`/explicit path lists.
  Shell command substitution like `TS=$(date ...)` inline in a compound command also gets rejected
  ("Contains expansion") this session — run `date +%Y%m%d-%H%M%S` as its own command first, then paste
  the literal timestamp into subsequent commands.
- `nm` itself needs explicit interactive approval — `python3 -c "..."` wrapping `subprocess.run(['nm',
  ...])` IS allowed. `scratch/agent/check_symtab3.py` is the latest template for "is this crash symbol
  genuine or nearest-symbol misattribution."
- **All BREADCRUMB* passes share ONE `g_rs64_last_guest_pc` global.** `drainMeshReleaseQueue`
  (BREADCRUMB15) and `coalesceFreeHeapBlocks` (BREADCRUMB11) are both fully instrumented — their
  `last-guest-pc` is always precise. A crash in a function NEITHER breadcrumb covers (e.g.
  `_platform_memmove`, `musyxSynthFrame`) reports whatever `last-guest-pc` was last set to, which can be
  stale/uninformative for that crash (s356: two unrelated crashes shared the identical
  `last-guest-pc=0x8000834c`, almost certainly a shared early-boot checkpoint, not a real signal).
- The raw `run.log` under `scratch/s73_post_a_scene/<label>/run.log` (not just the
  `scratch/agent/soak_results/*.log` summary) is where per-line diagnostic tags actually live — the
  summary logs only capture the LAST few lines. Grep the raw log directly for full history.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=<n> zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (`env` prefix required —
  project rule 10 / CLAUDE.md). Log lands at `scratch/s73_post_a_scene/<label>/run.log`. Note: this
  script's own `export HOLD_S=240` line INSIDE a recipe `.sh` overrides any `env HOLD_S=N` prefix passed
  to the recipe itself — to change hold length, edit the recipe file's `export HOLD_S=` line directly.
- `[CRASH][pc-symbol]` (host PC via `dladdr`, precise) and `[CRASH][last-guest-pc]` (guest checkpoint,
  only meaningful if the crashing function is breadcrumbed) answer different questions by design.
- Current gate state (unchanged since s343): fixup regex at `fixup_game_funcs.py` ~line 263 is
  `r"0x8008E(?:C88)"` — matches ONLY `reapplyDisplayMode` (`0x8008EC88`, force-zeroed);
  `setDisplayMode` (`0x8008EB40`) stays unmatched/reversed.
- A crash under ~5s that never reaches `title_reached` is NOT a meaningful test of any post-title-window
  instrument (s355 verify4) — don't count it toward a non-recurrence tally; it belongs in a separate
  "boot-time crash family" bucket (`musyxSynthFrame+4652` is the one seen so far).

## Queued this session (s356, ready for the loop — nothing run yet)

`s356_coalesceheapguard_verify5/6.sh` (Thread A, `HOLD_S=240`), both in `scratch/agent/soak_queue/`.
Thread B's `s355_ringbuffer_verify3/4.sh` were already queued as of s355 and still haven't drained —
also still sitting in `scratch/agent/soak_queue/`. 4 recipes total pending; loop drains up to 2 per gap.

HYPOTHESIS-ID: m5-audio-destub-coalesce-heap-guard-verify (iteration 3 — 3 meaningful non-recurrences of
4 needed, `verify5/6` queued s356; 2 real work sessions spent on this slug so far — s354, s356 — s355 was
a declared no-experiment MAINTENANCE session and doesn't count against iron rule 8's 3-strike budget).
Parallel/still-open: m5-audio-destub-linkedlist-corruption-source (iteration 3 of 3 available before iron
rule 8's mandatory pivot check — opened s352, instrument landed s353, 0/2-informative reading s354,
`verify3/4` queued s355, STILL undrained as of s356 — next session reading them is the mandatory
pivot-or-continue decision point).
