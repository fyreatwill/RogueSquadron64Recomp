# Next work unit

HYPOTHESIS-ID: m5-task-family-port-compare

Run one same-build port capture of the M5 OSTask `data_size` boundary and
compare it with the qualified retail result from s4886. Use the existing
`ROGUESQ_LOG_S4864` writer trace, task ABI rows, route-order/SP/PCM controls,
and the phase-gated AUTOPILOT recipe. Before building, keep these competing
hypotheses explicit:

1. H-port-cadence: the port's 1-dominant values are produced by the same
   `0x80149760` frame-batch counter but the port synth cadence advances it
   differently. Prediction: port writer/task values match, while the counter
   histogram differs from retail's 176/190 size-2-dominant sample.
2. H-port-publication: the port task staging or publication path changes the
   value after the guest writer. Prediction: port writer rows and `audtask-abi`
   rows disagree for the same phase/ordinal.
3. H-port-route: the previous port ratio was route or phase instrumentation
   bias. Prediction: qualified title/hangar controls are absent or the writer
   is not reached in the target phase.
4. H-counter-probe: the known `0x80091084` watch was simply the wrong
   instruction boundary. Prediction: a corrected probe at the generated
   counter read/loop head shows the value that explains each writer store.

Discriminator: one build and one port run must include the whole route-order
positive control, title/hangar VI phase controls, SP completion, nonzero PCM,
`ROGUESQ_LOG_S4864=1`, and the existing `audtask-abi` rows. Select H-port-
cadence only if writer and published task values match while the histogram or
counter cadence differs; select H-port-publication on a same-phase mismatch;
select H-port-route if controls fail; otherwise select H-counter-probe and
use the corrected counter/loop instrument. Do not change runtime behavior.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_S4562_PAUSE=0 ROGUESQ_LOG_S4864=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=110 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_AUDIO_UCODE=1 ./build/RogueSquadron64Recomp > scratch/agent/s4887_port_datasize.log 2>&1

Positive controls must be checked before interpreting any null. Kill the game
with SIGKILL after the phase-gated route completes or the watchdog expires.
