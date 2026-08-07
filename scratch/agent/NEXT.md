# NEXT work unit

HYPOTHESIS-ID: player-slot-anim-channel-idiom-class-s424

## s424 recap

Reproduction-confirmed (2/2, s423+its queued confirm soak) crash at `startPlayerSlotAnimationChannelLooping`
crossed NEXT.md's own pre-authorized bar for opening a root-cause session (second reproduction + systemic
argument: it blocks all forward M3 menu progress, not an M4-relocation edge case). Root-caused it: the
function derefs a global-cached pointer (`0x800CDFAC`) that's read back as plain `0x00000000` because its
only writer (`initCraftSelectScreen`) never runs before the first per-frame tick reads it — not pointer
corruption, an ordering/never-populated bug. Shipped a working guard (function+file-scoped
`fixup_game_funcs.py` patch, `[slot-anim-loop-guard]` tag) that verifiably stops the crash there, plus
write/read cache diagnostics (`[slot-anim-cache-write]`/`[slot-anim-cache-read]`). Live run: guard held,
0 writes / 1 read (0x0) / 1 guard-fire / 0 missing-func — then an IMMEDIATE sibling crash one call deeper
in the same tick: `advancePlayerAnimationPhase+564` (already on record as item -11, parked since s89,
"3 non-recurrences... 8 prior crashing soaks" — now recurred). Full detail: PORTING-STATE Session 424,
CURRENT-TRUTH item -261.

**Read this as an idiom class, not a single bug**: multiple sibling consumers of one
player-slot-animation-channel subsystem (confirmed: `startPlayerSlotAnimationChannelLooping`,
`advancePlayerAnimationPhase`; suspected per item -8's "shared-dispatcher hypothesis":
`frameStartReset`) all crash on the same never-initialized-before-first-tick root state during
`tickCraftSelectScreen`'s war-room per-frame handling. This matches the USER DIRECTIVE's preferred M3
shape (systematic idiom-class audit, the s282-s288 `-0x25A4` model) exactly — arrived at via the
crash-driven route this time, not a fresh discovery tool, but the same audit discipline applies.

## Competing hypotheses for what's actually happening

1. **Genuine call-ordering/race**: `tickCraftSelectScreen`'s per-frame handler (on thread id=8, entry
   `0x8006F2CC`, spawned right as the war-room screen appears) starts running before
   `initCraftSelectScreen`'s one-time setup (on the main game-loop thread) has populated this slot's
   channel — a scheduling race, consistent with this project's ~20+ already-catalogued nondeterministic
   corruption families (Method traps section).
2. **Slot-index mismatch**: `initCraftSelectScreen` DOES run and DOES populate a slot, but
   `tickCraftSelectScreen`/`drawRadarIcon` iterate a DIFFERENT slot index than the one that got
   initialized (e.g. iterates all N craft-select slots, but only one gets set up before the first tick,
   or the original N64 code has a per-slot "is this channel active" flag this recomp path skips).
3. **Never called at all on this driven path**: `initCraftSelectScreen` might legitimately only run in
   response to a specific menu-state transition this session's `PROBE_KEYS` schedule doesn't trigger in
   the right order (relevant given the still-open SELECT-GAME input-timing finding from s423 — schedules
   built by guesswork, not a confirmed-consumed-press signal).

**Discriminating measurement**: a same-build diagnostic at `initCraftSelectScreen`'s own ENTRY (not just
its write site) logging a counter + which slot index(es) it's called with, cross-referenced against
`tickCraftSelectScreen`'s per-tick slot index and thread id — would directly show whether
initCraftSelectScreen ever runs at all before the crash, and if so with which slot argument, splitting
H1/H2/H3 in one soak.

## Work unit for the next iteration

**Read `scratch/agent/SOAK-RESULTS.md` (tail) FIRST** for `s424_slotanimguard_confirm`'s verdict (queued
this session) before deciding whether to spend a live foreground run — if it already ran, fold its
write/read/guard counts into the picture below before choosing.

1. **Immediate, bounded, same pattern**: add an analogous wild-pointer guard to `advancePlayerAnimationPhase`
   (funcs_14.c, 0x80062B04 — same file, same idiom, same near-null-pointer signature expected) plus an
   entry-diagnostic on `initCraftSelectScreen` per the discriminating-measurement design above (both in
   the SAME build/patch batch — batch-instrumentation rule). This should either (a) get one function
   deeper still, surfacing `frameStartReset` or another sibling next, confirming the idiom-class read, or
   (b) actually clear the war-room transition and reach AVAILABLE CRAFT, which would be the first time
   this project has gotten that far.
2. **If (a) recurs a 3rd sibling**: stop adding one-off guards (iron rule 8 territory) and switch to a
   proper idiom-class audit — grep every consumer of the `0x800CDFAC` global / every function in the same
   contiguous `main_overlay.txt` block (`startPlayerSlotAnimationChannel` through `resetPlayerSlotAllChannels`,
   0x80062854-0x80063C6C) for the same "deref the arg before checking it's non-null/initialized" pattern,
   classify each site, and guard or prove-safe the whole class in one pass — the `-0x25A4` model.
3. **If (b) reaches AVAILABLE CRAFT clean**: this is real M3 DoD forward progress — update the goal-stack
   M3 entry, re-run the extended cutscene-reaching schedule from s423's original calibration attempt to
   see how much further the fixed path gets.

Regen recipe (already used this session, known-working):
```
cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py
# delete RecompiledFuncs/funcs_*.c (mandatory, item -20) before N64Recomp regen
zsh ~/Documents/Tools/RogueSquadron64Recomp/tools/agent/regen_n64recomp.sh
python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py   # verify new patch lines report xN, not "no changes"
cd ~/Documents/Tools/RogueSquadron64Recomp/build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8
```
Live-run schedule (same as s423/s424, known to reach the war-room phase):
```
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_LOG_RUNNER=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 \
    PROBE_LEAVE_OK=1 \
    PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start" \
    zsh tools/probe.sh <outdir> 300 2
```

## Soak queue

- `scratch/agent/soak_queue/s424_slotanimguard_confirm.sh` — queued this session, not yet run.
