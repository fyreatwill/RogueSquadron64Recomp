# Session 3361 — port callback-table writer/source census

The Debug target was rebuilt after extending the regeneration fixup to report
the two retail-observed writers not covered by the existing probe:
`0x80007968` and `0x80017D08`. The run used the validated LLE-only
AUTOPILOT/spin-yield recipe with host/task/PCM controls and VI gates.

Controls were positive: 135 host-boundary rows, 92 PCM source rows, 92 PCM
consumer rows, title VI `1024 @ 0x00790400`, and hangar VI
`512 @ 0x006AB400`. There were no `[CRASH]` or `[ABORT]` rows. The two
task/gate markers were not enabled by this recipe and are not treated as
controls.

The aggregate writer table reached target phases and paired the relevant
values:

| edge | guest PC | value | count |
|---:|---:|---:|---:|
| 4 | `0x80007928` | `0x80003250` | 1 |
| 4 | `0x80007928` | `0x8009123C` | 3 |
| 6 | `0x80007968` | `0x00000000` | 3 |
| 7 | `0x80017D08` | `0x00000400` | 4 |
| 7 | `0x80017D08` | `0x00000800` | 1 |

The existing pointer/registration controls also fired: `0x80091900` stored
`0x80007910`, and `0x8009BC50` stored `0x8009B5A8`. This is single-source
port runtime evidence, independently paired with session 3360's retail watch.
The third retail writer does not supply `0x8009123C` on the port route, and
`0x80007968` is the clear path. The problematic value is written by the
known `0x80007928` callback-table store, so the third-site hypothesis is
refuted. No behavior change was made.
