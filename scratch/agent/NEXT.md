# NEXT work unit (s2507) — identify the writer of joined AI-buffer payloads

HYPOTHESIS-ID: m5-pcm-payload-writer-provenance

## Single work unit

Run one phase-gated write-provenance census for joined AI-buffer entries
`0x166450..0x169450`, with image-DMA and PCM-consumer controls enabled.
Preserve writer PC, address, length/value, route ordinal, and event ordering;
do not change audio behavior or filter writes. Include the oracle whole-RDRAM
control only if a retail null is used.

## Competing hypotheses and discriminator

- `H-payload-guest-writer`: a legitimate generated guest CPU store writes
  nonzero bytes into a joined entry before AI consumption.
- `H-payload-rsp-writer`: a legitimate image/RSP DMA is the first nonzero
  writer into a joined entry before consumption.
- `H-payload-host-writer`: host-side PCM production writes the joined entry.
- `H-payload-unresolved`: no writer is observed, or controls/order are absent.

The discriminator is one same-run ordered table of all writes overlapping each
joined entry, followed by the first consumer event. A positive-control row must
show image DMA and PCM consumer observers firing. The earliest legitimate
nonzero writer class selects its hypothesis; absent controls or no attributable
writer selects unresolved.

## Exact commands

```sh
rg -n 'rs64_m5_pcm_writer|rs64_probe_audio_dma_write|queue_samples|MEM_[BHW].*0x166|166450|169450' src ../N64Recomp/fixup_game_funcs.py ../N64Recomp/RecompiledFuncs/funcs_*.c lib/N64ModernRuntime/librecomp/src
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Use the qualified `tools/probe.sh` route from s2506 with
`ROGUESQ_LOG_M5_AI_TABLE=1`, `ROGUESQ_LOG_M5_TASK_CONTRACT=1`, and
`ROGUESQ_LOG_PCM_BOUNDARY=1`; write the result to
`scratch/agent/s2507_m5_joined_payload_writer/audit.md`.
