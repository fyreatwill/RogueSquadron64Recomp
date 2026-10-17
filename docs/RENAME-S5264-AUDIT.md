# Session 5264 — `osYieldThread` classification

The bounded helper was run over `0x80037510..0x8003755C`:

```text
renamed 0 references in 0 files
candidate 0x80037510 osYieldThread: already-synchronized
```

Independent checks found:

- `../rogue_squadron64/symbol_files/libultra.txt` defines
  `osYieldThread = 0x80037510`.
- The generated tree contains no `func_80037510` placeholder, body, or
  overlay record. It has 20 direct call sites to `osYieldThread_recomp`.
- The companion decomp has the corresponding `src/libultra/os/yieldthread.c`
  `INCLUDE_ASM` entry, so this address is a libultra ABI routine rather than a
  generated game body available for renaming.

This selects H1: preserve the ABI name; no generated-symbol edit is needed.
The companion symbol is defined, but its implementation is supplied through
the libultra ABI/assembly boundary, not by a placeholder in the generated
function set.
