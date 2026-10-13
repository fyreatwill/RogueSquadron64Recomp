# Next work unit — requalify the default-B40 callback route

HYPOTHESIS-ID: m5-callback-route-requalification

Run one single-arm default-B40 real-audio capture from `build/` with the
compiled `ROGUESQ_LOG_S4700_CB=1` callback witness, phase controls, and the
validated LLE/solo/spin-yield configuration. Keep the existing title/hangar
autopilot route, avoid `ROGUESQ_LOG_ALL` and unrelated high-volume probes, use
SIGKILL cleanup, and retain callback registration/deregistration/synth-entry
controls.

Competing hypotheses and discriminator:

- H-route-valid: the default-B40 route reaches title 1024 and hangar 512, so
  callback-table rows can be interpreted in the target phases.
- H-route-stall: the route remains at VI 640, making target-phase callback
  parity unevaluable and leaving the audio-route blocker as the next issue.
- H-crash: the route crashes before VI 1024; classify the crash signature and
  do not attribute it to callback teardown without a deregistration row.

DISCRIMINATING MEASUREMENT: phase transitions are the split: both
`vi_width=1024 origin=0x00790400` and `vi_width=512 origin=0x006AB400`
select H-route-valid; VI 640 without either selects H-route-stall; an
unclean crash selects H-crash. Only after H-route-valid, compare each
`dereg-exit` table with later `synth-enter` rows. Callback registration,
deregistration, synth-entry, and phase logs are the positive controls.

Exact build command:

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
```

Exact route variables: `ROGUESQ_LOG_S4700_CB=1 ROGUESQ_A14_YIELD=1
ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1
ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1 PROBE_PHASE_WIDTH=1024
PROBE_PHASE_TIMEOUT=110 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1`.
