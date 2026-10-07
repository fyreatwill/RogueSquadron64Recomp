# Next work unit: restore the canonical route recipe for the 0x8008F900 body witness

HYPOTHESIS-ID: m5-step4-object-entry-body

Session 4183 reran the body witness with silent audio and then real audio. The
retail positive control and both retail target phases fired, but both port arms
stopped at VI width 320 in `spTaskSchedulerThread+9772` / guest
`0x8000834c`; no port body rows were qualified. The recipe still differs from
the earlier qualified canonical route in its autopilot schedule and lacks
`ROGUESQ_AUTOPILOT_STOP_WIDTH=512`.

Competing hypotheses:

- H-canonical-route-reaches-target: restoring the known event schedule and
  stop-width setting lets the port reach title and hangar, enabling the body
  tuple comparison.
- H-scheduler-crash-persists: the same pre-target scheduler crash remains;
  body mismatch versus parity is still unevaluable and the route boundary must
  be audited separately.
- H-retail-control-invalid: the independent control or retail phase gates fail;
  no port conclusion is allowed. (This would falsify the current route-invalid
  reading.)

Discriminator: one paired run after changing only the port recipe to
`ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'`
and adding `ROGUESQ_AUTOPILOT_STOP_WIDTH=512`. Preserve the whole-RDRAM
positive control, both title origins (`0x00790400`/`0x00790800`), both hangar
origins (`0x006AB400`/`0x006AB800`), and joined `0x8008F8FC`/
`0x8008F900` body rows. Target phases plus body rows enable the tuple test;
continued width-320 failure selects scheduler-route failure; missing retail
controls invalidates the run. Do not change audio, gate, writer, payload, or
mitigation logic.

Exact command: `zsh scratch/agent/run_s4182_m5_object_body.sh`.
