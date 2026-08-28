# Session 2988 — M5 buffer-arbiter repair A/B

The Debug build completed successfully. The first wrapper attempt failed before
launch because this checkout uses `build/`, not `build/Debug`; the corrected
wrapper launched both arms concurrently from `build/`.

| Measurement | Control | Repair (`ROGUESQ_FORCE_BUFFER_PROGRESS=1`) |
|---|---:|---:|
| process result | 0 | 1 (probe timeout) |
| LLE audio-task dispatches | 45 | 57 |
| VI phase transitions | 4 | 2 |
| final useful phase | 640 @ `0x0066A500` | 320 @ `0x006DD280` |
| title `1024 @ 0x00790400` | 0 | 0 |
| hangar `512 @ 0x006AB400` | 0 | 0 |
| route-state rows | 5 | 0 |
| target route/candidate rows | 0 | 0 |
| crash/abort markers | 0 | 0 |

The same-build task-dispatch positive control was active in both arms. The
repair arm degraded route progress from VI 640 to VI 320 and never reached
the handoff probe. This selects `H-repair-harmful` for this implementation and
rejects the forced 4→5→0 transition driver as an M5 route unblocker. It does
not identify the missing writer/signal; this mitigation-shaped experiment is
not an explanation.

