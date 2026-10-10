# NEXT: name which voice+0x34 store wrote 0x6C617465

HYPOTHESIS-ID: odd-dma-voice-store

s4534 closed the jal. Do not rebuild that probe and do not re-read the four calls. The aborting jal is `musyxRenderVoiceSamples` at `0x800903F0`. Delay slot changes a1 only. raw34 == a3 == `0x6C617465`. The +0x100 jals are not this abort: the same run's `0x800902CC` row had raw34+0x100 == a3 on a different value and returned. `0x6C617465` is not a legitimate cart offset. Do not add a skip. Do not grep the tree for other writers of voice+0x34.

The two named stores, both in `funcs_24.c`:

- `musyxKeyOnVoice` `0x80090C80`: `sw v1, 0x34(s1)`. v1 was loaded at `0x80090C74` from `0x38(s0)`. At the store, value is `ctx->r3`, voice is `ctx->r17`, source object is `ctx->r16`.
- `musyxInitVoiceFromSample` `0x800921E8`: `sw v1, 0x34(a0)`. v1 was loaded at `0x800921DC` from `0x4(a1)`. At the store, value is `ctx->r3`, voice is `ctx->r4` (already the computed slot), descriptor is `ctx->r5`.

One instrument, one build, one run. Gate it on a new env (do not reuse `ROGUESQ_LOG_S4534` as the gate; leave that probe in the binary and arm it too, so the bad jal row is the same-run join). Log immediately before each store. Print one bad row when the stored word is odd or its top byte is ASCII, and always print `0x6C617465` (cap 8). Print one in-range control per store (word `< 0x01000000` and even). Include the guest PC, the voice, the stored word, the source pointer, and the source word. Phase-scope nothing: the death is the 512-to-640 edge.

A same-run control is mandatory. s4534's ctl jal had raw34 `0x00C80000`, so a sane voice word does get stored. If a bad store row fires and no control row does, the log is not qualified. If the s4534 bad jal does not fire, the join is missing; do not conclude the stores are innocent.

Outcomes:

- Bad row at `0x80090C80` whose stored word is `0x6C617465` and whose voice equals that run's `[s4534-jal] kind=bad` s1: selects H-keyon. The copied source is s0+0x38. Stop. Do not add a skip. Do not instrument the init store further.
- Bad row at `0x800921E8` whose stored word is `0x6C617465` and whose voice equals that run's bad jal s1: selects H-init. The copied source is a1+4. Stop. Do not add a skip.
- Both stores print `0x6C617465` for that same voice: the later row is the producer. Quote both, in order, and stop.
- Both stores print an in-range control, neither prints `0x6C617465`, and the s4534 bad jal still fires on `0x6C617465`: selects H-neither. These two stores are not the producer. Stop. Do not grep for a third writer.
- Run dies in `do_rom_read` on `0x6C637265` with no s4534 bad row: the jal witness was not armed. Not a result about the stores.
- Run dies in `fillSampleStreamRange` with guest pc `0x8000834c` before VI 640: the parked bus error. Not this join. Do not re-run.
- Run never reaches VI 640: the edge was missed. Do not re-run the same recipe.

Use the s4534 route: `ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1`, the existing passive logs, `ROGUESQ_LOG_S4533=1`, `ROGUESQ_LOG_S4534=1`, and the new env. `PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1` and the same Start keys. Run `tools/probe.sh` from `build/` with the ROM beside the binary. Kill with SIGKILL.
