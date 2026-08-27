# Session 2680 M5 Step 1 re-baseline

The Debug build completed successfully. The existing
`run_s2618_hangar_pcm_boundary.sh` recipe ran image and silent arms
concurrently with the qualified LLE route, AUTOPILOT, `C88=0`, and
phase-gated probes. Both reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`; both were SIGKILLed by the 90-second watchdog. No crash
or abort marker occurred.

| phase-keyed field | silent `musyx_stub` | image `factor5_ucode_b` |
|---|---:|---:|
| title / hangar route controls | 1 / 1 | 1 / 1 |
| `audtask-dispatch` | 77 | 77 |
| `audtask-abi` / `audtask-dma-row` | 2332 / 2332 | 2275 / 2275 |
| image DMA ranges | 0 | 4764 |
| image-stage rows | 0 | 14328 |
| audio return | 526 | 526 |
| audio route / SP route | 2340 / 2340 | 2301 / 2301 |
| PCM source / consumer | 98 / 98 | 98 / 98 |
| sampled PCM payload | `fnv=F59C39C5`, `nz=0` | `fnv=F59C39C5`, `nz=0` |
| crash / abort | 0 / 0 | 0 / 0 |

The image arm alone did real DMEM/DMA/image-stage work and reached
`break_pc=0x1328`, but that activity produced no image-only service, slot,
voice/MORT, route, or PCM edge in this capture. This selects `H-ContractGap`
at the measured downstream boundary; it rejects `H-RouteOnly` and
`H-AudioDegeneracy` there. No writer, output destination, writeback, remap,
gate, or mitigation was changed.

Raw logs: `scratch/agent/s2618_m5_hangar_pcm_boundary_rerun/{image,silent}.log`.
