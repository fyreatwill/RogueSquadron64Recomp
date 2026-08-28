# s2886 M5 route/contract discriminator

The Debug target was rebuilt once, then the image (`ROGUESQ_AUDIO_UCODE=1`)
and silent (`=0`) arms ran concurrently with the same phase-gated contract
instrumentation and validated autopilot. The retail oracle ran separately with
the whole-RDRAM positive control.

| Measurement | Retail oracle | Image arm | Silent arm |
|---|---:|---:|---:|
| Whole-RDRAM positive control | 10,000 callbacks; 10,105 lifetime writes | n/a | n/a |
| Target route | title 1024 and hangar 512 reached | not reached | not reached |
| Last port route | n/a | 640 @ `0x0066A500` | 640 @ `0x0066A500` |
| M_AUDTASK dispatch | n/a | 66 | 66 |
| Route preparations | n/a | 6,869, all accepted=0 | 6,886, all accepted=0 |
| Route-state rows | n/a | 5, all pre-title | 5, all pre-title |
| Stage-call rows | n/a | 68, all pre-title | 0 |
| Task/DMA/image/service/slot/MORT/PCM rows | not watched in this unit | 0 | 0 |
| Crash/abort | n/a | 0/0 | 0/0 |

The oracle writer watch for `0x8006E4B4` produced six boot-time execution hits
and no phase-gated field rows; the independent state-span watch produced 105
writes and the target phases. Thus the candidate remains a write-attributed
retail route lead, not a callable target-phase contract edge.

Conclusion: H-RouteInvalid is selected for this recipe. Downstream audio nulls
are unevaluable, and no behavior change is authorized. The repeated route stop
also triggers the required pivot away from this route hypothesis.
