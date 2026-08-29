# Session 3153 — Step 6 drain-policy qualification

| Arm | Gate rows | Phase rows | Shade-DMA controls | Crash/abort | Last phase |
|---|---:|---:|---:|---:|---|
| default, env unset | 0 | 4 | 8 | 0 | VI 640, `0x0066A500` |
| `ROGUESQ_DRAIN_INLOOP_TICK=1` | 0 | 4 | 8 | 0 | VI 640, `0x0066A500` |

Both Debug-binary arms ran concurrently from `build/` for 30 seconds. The
shade-DMA rows are a runtime-positive control that capture and pre-title
execution were active. The drain-gate positive control failed in both arms,
so neither policy value can be inferred. Neither arm reached title 1024 or
hangar 512; task, slot, voice, and PCM nulls remain unevaluable.
