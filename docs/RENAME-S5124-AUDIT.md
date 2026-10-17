# Generated-symbol audit — Session 5124

Candidate: `osCreateThread = 0x8002B330`

The bounded helper command was:

```text
python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x8002B330 --end-address 0x8002B480
```

It reported `renamed 0 references in 0 files` and classified the companion
entry as `already-synchronized`.

Independent checks select the host-wrapper/ABI-boundary outcome:

- `RecompiledFuncs/funcs.h` declares `osCreateThread_recomp`, but no generated
  `func_8002B330` or `fake_func_8002B330` body exists in `funcs_*.c`.
- `recomp_overlays.inl` records `osCreateThread_recomp` at offset `0x2AEF0`
  with `rom_size = 0`; the next companion entry is `osDestroyThread` at
  `0x8002B480`.
- The companion `libultra.txt` names the address `osCreateThread`, while the
  generated tree contains 10 direct `_recomp` call sites in 4 generated
  files. These are callers of the runtime wrapper, not evidence of a
  generated function body.

Decision: preserve `osCreateThread_recomp`; no mapping, build, or soak is
warranted. The next candidate is `osDestroyThread = 0x8002B480`.
