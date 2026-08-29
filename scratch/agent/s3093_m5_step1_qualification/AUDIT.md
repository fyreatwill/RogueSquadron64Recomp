# Session 3093 — M5 Step 1 qualification

## Work unit

Re-baseline the current Factor 5 image arm against the same-build silent
`M_AUDTASK` control before changing any audio contract edge.

## Controls and recipe

- Debug target rebuilt with `cmake --build build --config Debug --target RogueSquadron64Recomp`.
- Retail oracle ran with whole-RDRAM write control, title/hangar VI tracing,
  and the existing start schedule.
- Port used the existing AUTOPILOT and phase-gated M5 marker set. Silent used
  `ROGUESQ_AUDIO_UCODE=0`; image used `ROGUESQ_AUDIO_UCODE=1`. Both arms were
  launched concurrently from the same rebuilt binary.

## Positive controls

The retail oracle reached the whole-RDRAM threshold (`watch index 0
callbacks=10000`), title `1024 @ 0x00790400`, and hangar
`512 @ 0x006AB400`. The port dispatch control fired in both arms: 78
`audtask-dispatch` rows in the silent arm with `real_ucode=0` and 78 in the
image arm with `real_ucode=1`. The run had live retail and port instruments;
downstream zeroes are not treated as absent instrumentation.

## Result table

| Field | Silent arm | Factor 5 image arm |
|---|---:|---:|
| Audio dispatch rows | 78 | 78 |
| Dispatch arm | `real_ucode=0` | `real_ucode=1` |
| Last port VI phase | 640, `0x0066A500` | 640, `0x0066A500` |
| Title phase | 0 | 0 |
| Hangar phase | 0 | 0 |
| Task ABI / DMA / image-stage rows | 0 | 0 |
| Audio return / service / PCM rows | 0 | 0 |
| Crash / abort markers | 0 / 0 | 0 / 0 |

## Hypothesis decision

The identical pre-title route boundary in both audio arms rejects
H-ArmDivergence: changing only the selected `M_AUDTASK` arm did not alter
route reachability. H-AudioDegeneracy and H-ContractGap remain unevaluable at
the required title/hangar phases because neither arm reached them; no claim
about DMEM/DMA correctness, service, slot, voice, MORT, or PCM behavior is
authorized. The selected result is H-SharedRouteBoundary: the next
discriminator must move upstream of the audio target phase to the VI-mode
publication/consumer handoff.

No audio behavior, gate, wait, voice guard, or output destination changed.

Evidence and full logs: `driver.log`, `oracle.log`, `silent.log`, and
`image.log` in this directory.
