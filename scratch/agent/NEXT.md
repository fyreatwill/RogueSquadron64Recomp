# NEXT work unit (s2498) — test separate slot/voice-to-PCM contract

HYPOTHESIS-ID: m5-generated-image-downstream-join

## Single work unit

Perform one phase-keyed port/oracle capture of the separate slot/voice-to-PCM
contract. Use the qualified image arm at width 512 / origin `0x006AB400` with
the existing positive controls, and join each first nonzero PCM consumer to
the preceding retail-writer address range and the port's first slot/key-on
event fields. Use the oracle whole-RDRAM, hangar, and named-PC controls before
interpreting any retail null. Do not infer an image identity from ordering and
do not change behavior.

## Competing hypotheses and discriminator

- H-slot-writer: the PCM consumer address is written by the retail-equivalent
  slot/voice path and the port event row identifies that same contract.
- H-image-independent-voice: the port PCM consumer is valid but is fed by a
  voice/slot source unrelated to the image-stage ranges and retail writer.
- H-no-consumer-contract: neither side yields a phase-valid writer-to-consumer
  join after all controls pass.

The discriminator is one phase-keyed table containing port consumer address,
length/hash, guest-writer PC/address/value, first slot/key-on site and event,
and the corresponding retail writer PC/address/value. A writer/address join
on both port and retail selects `H-slot-writer`; a valid port consumer with
nonmatching writer/slot identity selects `H-image-independent-voice`; passed
controls with no writer-to-consumer join select `H-no-consumer-contract`.
Build all fields in one capture; do not add another breadcrumb unless this
table leaves two hypotheses indistinguishable.

## Exact commands

Build/run the existing qualified probe with its passive breadcrumbs and the
port PCM/writer/slot logs enabled; run the matching oracle recipe with its
whole-RDRAM, hangar, and named-PC controls. Write the joined table and
conclusion to `scratch/agent/s2498_m5_slot_voice_pcm_join/audit.md`.

```sh
rg -n "m5-guest-writer|m5-second-range|pcm-boundary-consumer|audtask-image-downstream|keyon-w40|slot-sb|DebugSetCallbacks|800078EC|166450|169150|1798B0|179A48" src lib tools/oracle
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 zsh tools/run-qualified-probe.sh
```

Use the repository's existing oracle recipe with whole-RDRAM, hangar, and
named-PC controls in the same iteration; kill both runs with SIGKILL.
