# NEXT work unit

HYPOTHESIS-ID: item-316-dl-alloc-propagation-guard-confirm

## s489 summary: item -316 fixed (DL_ALLOC_PROPAGATION_GUARD), 1st confirm clean, 2nd queued

s488's sub-threshold `-0x5BB4` idiom candidate (19 read sites, `funcs_3.c`/`funcs_4.c`) resolved into
a real fix, one function upstream of all 19 reads. A downstream-consumer trace (delegated to a
subagent) found the actual gap in `emitAllocatedDLCommand` (`funcs_3.c`): its existing s436
`CACHE_HEAD_A1_GUARD` (site=4, 0x80008960) validates a newly linked free-list node pointer before
writing the node's own `next` field, but two more statements immediately after the guard block stay
UNCONDITIONAL even when the node pointer fails the range check: one publishes the possibly-bad node
as the new list head, the other propagates the node's data-area pointer into the persistent
`-0x5BB4` write-cursor global that all 19 read sites reload unguarded. Confirmed real downstream risk
by reading `buildOrientedFaceGeometry` (one of the 19 readers): it reloads the cursor, adds a scaled
index, and feeds the sum straight into `do_swl`/`do_swr` as a raw, unbounded RDRAM address. Exactly
the "guard covers one deref, not the propagation" shape as items -312/-313/-314/-315 — same fix
style: extended the check (`DL_ALLOC_PROPAGATION_GUARD`, `fixup_game_funcs.py`, s489) rather than
adding 19 read-site guards, after confirming (full function-body read) that both newly-guarded
statements are the function's last use of the relevant registers before its immediate
stack-restore-and-return tail.

Regenerated in the mandatory order, patch applied x1 with no anchor-count mismatches anywhere in the
fixup report, build-verified clean. Live-verified with the full standing sibling-guard env-var set
plus the new `ROGUESQ_LOG_DL_ALLOC_PROPAGATION_GUARD`: 0 fires on the new guard, 0 fires on any
sibling guard family (no regression), `hangarbay-entry` positive control fired (n=31, lower than
usual only because the run was cut short at 113s). Crashed at 113.2s,
`pc-symbol=initVec4TripletFromArgs+68`, `last-guest-pc=0x800ab068` — the exact same `last-guest-pc`
as the already-catalogued s463/s468 crash family, unrelated to this fix, filed not chased. 2nd
independent confirm queued (`s489_dl_alloc_propagation_confirm.sh`, currently the only item in
`soak_queue/`).

## This session's next work unit

1. Read the new `SOAK-RESULTS.md` line for `s489_dl_alloc_propagation_confirm` (the loop will have
   run it between iterations). Fold it into `docs/CURRENT-TRUTH.md` item -316 and `PORTING-STATE.md`
   the same way s488 folded in item -314's 2nd confirm: if clean (0 fires on the new guard, crash — if
   any — matches an already-catalogued unrelated family), mark item -316 fully CLOSED, 2/2. If it
   fires or reveals a NEW sibling scope gap (the -312..-315/-316 lineage's repeated pattern: closing
   one gap surfaces a structurally-identical one elsewhere), treat that as the next work unit under
   the same investigative standard (2 direct source reads before proposing a fix).
2. If item -316 closes clean with nothing new surfaced: no fresh M3 idiom-scan candidate remains
   queued (`lui`+`lw` and `lui`+`sw` are both structurally dry at the >=20-site tier as of s488). Two
   options, pick whichever has higher expected value at the time:
   - Re-run the M5 lead-check cadence (last checked s488; due again once 3+ sessions have passed —
     check `PORTING-STATE.md`'s most recent session number against s488 first).
   - Try a NEW frequency-scan angle not yet mined: the s465/s477/s481-488 lineage only scanned
     `lui`+`lw` and `lui`+`sw` reg-offset idioms. Consider `ori`/`addiu`-based small-offset pointer
     arithmetic, or lowering the site-count floor further (5-9 sites) with tighter manual triage per
     bucket, matching the same "grep-enumerate a whole idiom class, classify every site" discipline
     from `tools/agent/ITERATION.md`'s strategic priority #3.

## Regen/build/soak recipe (only needed if a new fix is designed — reading SOAK-RESULTS.md needs
neither)
`python3 -c "import glob,os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
→ `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` → `cd ~/Documents/Tools/N64Recomp
&& ./build/N64Recomp rogue_squadron.toml` → `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py`
(check the report for the expected counts, no errors, no SKIPPED lines) → **`cd
/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build`** (NOT `~/Documents/Tools/N64Recomp/build`
— that's the recompiler CLI's own build and silently no-ops) →
`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`. Arm every sibling
guard env var per the standing rule — see
`scratch/agent/soak_queue/done/s489_dl_alloc_propagation_manual_20260807.sh` for the current full
list, add `ROGUESQ_LOG_<NEW_GUARD_NAME>=1` for whatever the new guard is named.

## Soak queue status
1 item queued: `s489_dl_alloc_propagation_confirm.sh` (item -316's 2nd independent confirm).
