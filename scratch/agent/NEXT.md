# NEXT work unit (s1976) — fix drainAudioAndFinalizeSpeechBuffer infinite spin

HYPOTHESIS-ID: hangar-frame-freeze

## What s1975 settled

Root cause of update_screen #2176 freeze: `drainAudioAndFinalizeSpeechBuffer` (#17, the
final drain after the craft-select screen completes) spins forever because `tickMusyXIfActive`
(called once before the spin) submits no RSP audio task — MusyX is in shutdown/idle state at
that point. Every `anyAudioSlotActive` call in the spin returns 0. Audio tick eventually blocks
in `do_recv(0x80114388)` at vi-cb-recv1 n=1970.

Evidence chain:
- No `[lle task]` from main game thread between slot-ret-caller n=16 exit and update_screen #2176
- spin-yield n=1,2,3 fired (300k iters), vi-cb-recv1 ran synths n=2199-2204, none activated slot
- vi-wait counter stopped at n=8113; no game events for full 120s probe after n=1970 blocks
- Caller (funcs_34.c:0x800C5E88): do { tickCraftSelectScreen(); } while (r16==0xFFFFFFFF);
  then drainAudioAndFinalizeSpeechBuffer() — drain #17 is the "screen done" drain

H-vi-queue-full REFUTED; H-game-recv-blocks CONFIRMED (audio tick variant); H-yield-missing
REFUTED.

## Fix to implement

In `tools/fixup_game_funcs.py`, locate the existing s1972 spin-yield patch for
`L_800B24D4` inside `drainAudioAndFinalizeSpeechBuffer` (`funcs_30.c`). Add two
new insertions at the same label:

1. Call `tickMusyXIfActive` inside the spin loop — add it AFTER the yield gate, BEFORE
   `anyAudioSlotActive` is called. This matches the `menuControllerInput` (L_800B8050)
   pattern which already calls both in each iteration. With tickMusyX inside the loop,
   MusyX will eventually submit a task and activate a slot.

2. Add a safety timeout (only if anyAudioSlotActive hasn't returned true after 10M iters,
   break with a warning log). Prevents a regression to infinite spin if MusyX truly cannot
   produce audio.

Exact patch location in `funcs_30.c`:
- Function: `drainAudioAndFinalizeSpeechBuffer` (RECOMP_FUNC at line 11098)
- Label: `L_800B24D4` (line 11114)
- Current patch block: lines 11115-11133 (spin-yield gate s1972)
- New insertion: between the yield gate and the `anyAudioSlotActive` call (line 11137)

The fixup pattern should look like:

```python
# In fixup_game_funcs.py, within the L_800B24D4 patch:
# After existing spin-yield block, before anyAudioSlotActive:
"    { // PATCH s1976: tickMusyXIfActive inside drain spin\n"
"        static int drain_tickmusyx_en = -1;\n"
"        static long long drain_spin_iters = 0;\n"
"        if (drain_tickmusyx_en < 0) { const char* e = getenv(\"ROGUESQ_DRAIN_TICK_MUSYX\"); "
"drain_tickmusyx_en = (e && e[0] && e[0] != '0') ? 1 : 0; }\n"
"        ++drain_spin_iters;\n"
"        if (drain_tickmusyx_en) { tickMusyXIfActive(rdram, ctx); }\n"
"        if (drain_spin_iters > 10000000LL) { "
"fprintf(stderr, \"[drain-timeout] drainAudioAndFinalizeSpeechBuffer exceeded 10M iters, breaking\\n\"); "
"fflush(stderr); break; }\n"
"    }\n"
```

Make `ROGUESQ_DRAIN_TICK_MUSYX` default-on (check if `e == NULL || e[0] == '0'` to disable).
The env gate lets it be turned off for isolation but should be on by default since the root
cause is confirmed.

Alternatively, since the root cause is confirmed and tickMusyXIfActive in a loop is the
correct N64 pattern (matching menuControllerInput), make it unconditional + just keep the
timeout as a safety net.

After patching: follow the regen order (make_elf.py is not needed for fixup-only changes;
just re-run fixup_game_funcs.py and cmake rebuild).

**Regen note:** fixup_game_funcs.py edits regenerated C. Just rebuild:
```sh
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build
python3 ../tools/fixup_game_funcs.py ../N64Recomp/RecompiledFuncs/
ninja RogueSquadron64Recomp
```

## Exact test

Run a 120s probe after the fix:
```sh
mkdir -p scratch/agent/s1976_drain_fix_probe
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1976_drain_fix_probe 120 2
```

Success criteria:
- `[slot-ret-caller] site=drainAudioAndFinalizeSpeechBuffer n=17` appears in the log
- `fs` advances past 1256 after update_screen #2176
- No new crash family introduced
- Positive control: spin-yield n=1,2,3 still fire (drain IS still spinning briefly, then resolves)

If drain timeout fires (`[drain-timeout]`): tickMusyXIfActive is still not submitting a task
inside the loop — root cause is deeper (MusyX state issue). Log the drain iter count and
investigate tickMusyXIfActive's internal condition.

## Iron rules for this unit

- Do NOT change the spin condition (it is correct: wait for slot to become active).
- Do NOT add a blanket "break after N iters" without logging — silent skip would hide regression.
- The fix is an unconditional code-path change within fixup_game_funcs.py. No new env gate
  needed for the tickMusyXIfActive call (root cause is confirmed); keep the timeout.
- Positive control required: verify spin-yield n=1,2,3 STILL fire (confirms drain still spins
  initially, then resolves — not bypassed by timeout).
- Single game run. Build once. If build fails, diagnose before re-running.
