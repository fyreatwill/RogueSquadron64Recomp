# Next work unit

HYPOTHESIS-ID: m5-audio-destub

Run one complete status-table writer attribution census for M5 Step 7. The
previous qualified route reached `serviceVoicePoolFrame` with status `03`,
then later read status `00`, but did not identify the zeroing writer or a
shutdown call-3 return.

Competing hypotheses:

- H-status-writer: the candidate worker writes zero to the exact status-03
  slot and call 3 returns.
- H-status-source: another generated path writes zero, or the candidate uses
  a different table/slot address.
- H-status-unjoined: status becomes zero through a path outside the current
  worker/call-3 instrumentation, so the observed transition is not yet a
  proof of the shutdown contract.
- H-status-legitimate: status 03 is a legitimate persistent state for some
  slots; every observed zero must be tied to its exact slot and caller.

Discriminating measurement: one build/run with a static census and phase-gated
runtime probes for every generated store to `D_80154620` (PC, exact address,
old/new value, slot), `stopVoiceSlotSynced`, `serviceVoicePoolFrame` entry and
exit, shutdown call-3 entry/return, slot transitions, task/SP completion, PCM,
VI, and whole-RDRAM controls. Worker entry -> exact status-03 zero store ->
call-3 return selects H-status-writer. A different exact writer/address selects
H-status-source. A zero transition without either join selects H-status-unjoined.
Persistent 03 with the legitimate slot/caller context selects
H-status-legitimate. Missing rows are invalid unless title, hangar, and both
positive controls fire.

Before building, enumerate all generated stores and existing anchors:

    rg -n -C 6 '80154620|154620|stopVoiceSlotSynced|serviceVoicePoolFrame|shutdownMusyXVoices' RecompiledFuncs tools/fixup_game_funcs_vendored.py docs/M5-AUDIO-PLAN.md

Build and run the qualified recipe after adding the complete store table to
the existing batch:

    cmake --build build -j8
    zsh scratch/agent/run_s4117_m5_status03_silent.sh

Require title `0x00790400`, hangar `0x006AB400`, retail whole-RDRAM control,
and same-phase writer/worker/call-3 joins before selecting an explanation.
Do not change the wait or force-clear status. Use SIGKILL for cleanup.
