# NEXT work unit — trace the upstream producer feeding caller s0

HYPOTHESIS-ID: m5-output-state-contract-boundary

The corrected title callsite join selected producer/input: port `rs_free`
preserves pre-call `s0` at `0x80001C98` in all 514 captured rows, including 480
rows from caller `0x80005268`. Find the upstream writer/input supplying that
caller-side register context.

Competing hypotheses and discriminating outcomes:

- `H-UpstreamProducer`: a phase/ordinal-joined producer row already differs in
  `s0`;
  selects the missing producer/input contract.
- `H-WrapperClobber`: producer-side `s0` matches but target-entry `s0` differs;
  selects wrapper register capture or ABI clobber.
- `H-ProducerJoinAbsent`: controls fire but producer rows cannot be joined by
  title phase, producer PC, target PC, and ordinal; result is unevaluable.
- `H-ControlFailure`: the producer table's positive control is absent; repair
  the control before interpreting any null.

Build one instrument containing the upstream producer PC, callsite PC, target
PC, per-target ordinal, `s0`, `s1`, source word, branch selector, branch state,
and output/state fields; retain the existing four-PC positive-control marker.
The next exact build/run is:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_STATE_POINTER=1 ROGUESQ_LOG_M5_OUTPUT_STATE_FIELDS=1 sh -c 'cd build; ./RogueSquadron64Recomp > ../scratch/agent/s3455_port_upstream.log 2>&1 & p=$!; sleep 25; kill -KILL "$p" 2>/dev/null || true; pkill -KILL -x RogueSquadron64Recomp 2>/dev/null || true; wait "$p" 2>/dev/null || true'

Join the new port rows to `scratch/agent/s3454_oracle_caller.log` by phase,
producer/callsite PC, target PC, and ordinal. If the new producer value differs,
`H-UpstreamProducer` is confirmed; if it matches but target entry differs,
`H-WrapperClobber` reopens; absent ordered producer rows select
`H-ProducerJoinAbsent`; missing control selects `H-ControlFailure`. Do not
alter waits, slots, dispatch, clear behavior, or PCM writeback.
