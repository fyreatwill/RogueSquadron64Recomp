# s2584 M5 port writer/value correspondence

## Work unit

One qualified image-arm port capture correlated phase-keyed PCM writer/value
rows with the independent retail candidate ranges from s2583. No port code,
task field, output pointer, gate, or mitigation changed.

## Controls

- Debug target built successfully with `cmake --build build --config Debug
  --target RogueSquadron64Recomp`.
- The configured macOS artifacts were `build/RogueSquadron64Recomp` and
  `build/rogue_squadron.z64`; the stale `build/Debug/...` path was corrected
  after the first launch attempt.
- The fixed capture observed both target phase controls: title
  `vi_width=1024`, origin `0x00790400`, and hangar `vi_width=512`, origin
  `0x006AB400`.
- Positive runtime controls fired: 48 `[audtask-dispatch]` rows, 64
  `[runner-step]` rows, and Factor 5 task/image runner completion rows.

## Discriminator table

| phase | port PCM rows | nonzero samples | port writer rows | writer fields | retail comparison |
|---|---:|---:|---:|---|---|
| title `1024 @ 0x00790400` | 40 source + 40 consumer | 0 | 0 | `writer_pc=0`, `writer_phys=0`, `writer_writes=0`, value `0` | retail writer `0x8008ED48`, post-store `0x01000000` |
| hangar `512 @ 0x006AB400` | 30 source + 30 consumer | 0 | 0 | same zero writer fields | retail writer `0x8008ED48`; `0x141AD0` writer `0x80094648` |

The 70 source and 70 consumer rows were produced by the same run. The
phase-keyed join rows carried zero-valued 384-sample/768-byte buffers and no
writer attribution in both phases. No port event matched either retail
writer/value boundary.

## Result

`H-PortWriterMissing` is selected at the current observable boundary. The
port-side PCM source/consumer path is live, but the candidate guest writer
event is absent before those joins. This is supported by two independent
lines: the port runtime capture and the retail oracle writer/value capture
from s2583. It does not identify which port store or task contract is wrong,
and authorizes no mitigation or data rewrite.

Artifact: `scratch/agent/s2584_m5_port_writer_value.log`.
