# NEXT work unit

## s357: Thread B landed informative ring-buffer data (crash inside `drainMeshReleaseQueue`, past both
## existing guards, exact `last-guest-pc=0x80008200` repeat of s351), source-proved and guarded a 2nd
## unguarded tail-scan loop in the same function. Queued verify soaks for the new guard.

Full detail: `PORTING-STATE` Session 357, `docs/CURRENT-TRUTH.md` item -212.

`s355_ringbuffer_verify4` (drained by s357's session start) crashed at
`pc-symbol=drainMeshReleaseQueue+3140`, `last-guest-pc=0x80008200`, with `read_guard_fire_n=1`,
`write_guard_fire_n=1` (positive control — both existing guards fired earlier in the run) and
`ring_fire_n=1` (the ring breadcrumb's first-ever informative fire, showing `iter_at_bail=1,
v1[0]=0x00010001` — the same poisoned value from item -208, now confirmed at a 3rd independent
session/build). Cross-checking found `s351_drainmeshwriteguard_verify1` (Session 352) crashed at the
SAME `last-guest-pc=0x80008200` (different host offset, `+2864` vs `+3140` — consistent with the same
guest instruction inside a tight loop). Source-read found a SECOND, separate unguarded tail-scan loop in
`drainMeshReleaseQueue` (`funcs_3.c` ~1885-1889, guest `0x800081FC`/`0x80008200`, walking a
`ctx->r4`-rooted list distinct from the `ctx->r3` chain s350/s350b already guard) and added a
range-check-and-bail guard at the confirmed crash site (`0x80008200`) — new tag
`[drain-mesh-loop2-guard]`, reuses `ROGUESQ_LOG_DRAIN_MESH_TAIL_GUARD` (armed by default). Full regen +
rebuild clean. Queued `s357_drainmeshloop2guard_verify1/2.sh`.

## Two open threads — pick whichever has drained data first

**Thread B: `m5-audio-destub-linkedlist-corruption-source` (iteration 4 — landed a source-proved fix this
session, not a null reading; NOT subject to iron rule 8's pivot pressure since it discriminated).**
- **Step 1**: `s357_drainmeshloop2guard_verify1/2.sh` are queued in `scratch/agent/soak_queue/`
  (`HOLD_S=240`) — let the loop drain them, do NOT run inline.
- **Step 2 (next session)**: read whichever drained. Check `loop2_guard_fire_n`:
  - If `loop2_guard_fire_n>=1` in a run that also shows `last_pc_symbol` OUTSIDE
    `drainMeshReleaseQueue` (or a CLEAN run): positive control confirmed, crash relocated/resolved — same
    pattern as every prior drain-mesh guard. Good sign, needs a couple more non-recurrence soaks before
    calling it validated (4-meaningful-run bar per s348's precedent).
  - If `loop2_guard_fire_n>=1` but `last_pc_symbol` is STILL `drainMeshReleaseQueue+*` at a NEW offset:
    same s350→s351 downstream-relocation pattern — source-read the new offset, likely the flagged
    `0x800081FC` sibling read (pre-update v1) or a 3rd site; guard it following the same idiom.
  - If `loop2_guard_fire_n=0` and the run crashes at `pc-symbol=drainMeshReleaseQueue+3140` /
    `last-guest-pc=0x80008200` AGAIN: guard regex mismatch — re-check `funcs_3.c` around
    `0x80008200` in the regenerated source (should show `[drain-mesh-loop2-guard]` — if it doesn't, the
    regen didn't actually apply the patch this session; re-run the fixup and diff).
  - If a run shows `ring_fire_n>=1` (2nd informative ring sample): compare its `iter_at_bail`/`v1[0]`
    against this session's `iter_at_bail=1, v1[0]=0x00010001` — consistent supports the structural-bug
    reading, differing supports state-dependent corruption. This is the ORIGINAL Thread B discriminator,
    now finally answerable.

**Thread A: `m5-audio-destub-coalesce-heap-guard-verify` (iteration 3 — 2 clean + 2 off-target, 0/4
target-crash recurrences, 3 of 4 meaningful non-recurrence runs, 1 short of the 4-run bar).**
- **Step 1**: `s356_coalesceheapguard_verify5/6.sh` are queued in `scratch/agent/soak_queue/` — still
  undrained as of s357 session start. Let the loop drain them.
- **Step 2 (next session)**: same decision tree as before (see item -211 in CURRENT-TRUTH for the
  Step 2/2b/2c/2d branches) — count only meaningful runs (title-reached or long-hold crashes, not <5s
  boot deaths) toward the 4-non-recurrence bar.
- **Note**: if either hits `pc-symbol=_platform_memmove+96` again — that's the 2nd independent hit on
  s356's novel signature, the trigger to open a 3rd thread per s356's NEXT.md.

**Recommendation**: 4 recipes total pending across both threads (2 Thread A, 2 Thread B), loop drains up
to 2 per gap. Next session: read whichever pair(s) drained, resolve per the steps above. Thread B is the
higher-information-value read given this session's breakthrough — prioritize it if both pairs drained.

## Notes carried forward
- `[CRASH][pc-symbol]` (host PC via `dladdr`, precise) and `[CRASH][last-guest-pc]` (guest checkpoint,
  only meaningful if the crashing function is breadcrumbed) answer different questions by design.
- Current gate state (unchanged since s343): fixup regex at `fixup_game_funcs.py` ~line 263 is
  `r"0x8008E(?:C88)"` — matches ONLY `reapplyDisplayMode` (`0x8008EC88`, force-zeroed);
  `setDisplayMode` (`0x8008EB40`) stays unmatched/reversed.
- A crash under ~5s that never reaches `title_reached` is NOT a meaningful test of any post-title-window
  instrument — don't count it toward a non-recurrence tally; it belongs in the "boot-time crash family"
  bucket (`musyxSynthFrame+4652` is the one seen so far).
- **Implementation gotcha for future `fixup_game_funcs.py` patches**: `re.subn`'s plain-string
  `repl` argument gets backslash-escape-processed by the `re` module itself (`\n` → real newline, etc.) —
  ALWAYS use a lambda callback for multi-line replacement text containing `\n`/`\t`/etc. inside embedded
  C string literals (e.g. `fprintf` format strings). Every existing multi-line patch in the file already
  does this; s357 hit the bug once by not following that pattern and caught it via a failed build (not
  silently wrong output) — but re-verify after any future new patch by grepping the regenerated `.c` file
  for the new diagnostic tag string and confirming it's on one line, not just trusting a `patched xN`
  report line.

## Queued this session (s357, ready for the loop — nothing run yet)

`s357_drainmeshloop2guard_verify1/2.sh` (Thread B, `HOLD_S=240`), both in `scratch/agent/soak_queue/`.
`s356_coalesceheapguard_verify5/6.sh` (Thread A) still undrained, also still queued. 4 recipes total
pending; loop drains up to 2 per gap.

HYPOTHESIS-ID: m5-audio-destub-linkedlist-corruption-source (iteration 4 — landed a source-proved fix
this session on informative data, not a null reading; verify soaks queued s357). Parallel/still-open:
m5-audio-destub-coalesce-heap-guard-verify (iteration 3, 3 of 4 meaningful non-recurrences, `verify5/6`
still undrained as of s357).
