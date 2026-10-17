# Generated-symbol audit — `osSetIntMask`

Candidate: `osSetIntMask = 0x80033630`

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. The companion symbol map places
`osSetThreadPri = 0x800336E0` next, giving a nominal `0xB0` span, but the
generated tree contains no function body or placeholder at `0x80033630`.
It contains only the ABI declaration in `funcs.h` and a zero-size overlay
record; there is no direct generated caller. This is an unmaterialized
libultra/ABI entry, so preserve the ABI name; there is no body span to
validate or rename.

Evidence commands and results:

```text
rg -n 'osSetIntMask|func_80033630|fake_func_80033630' ...
(funcs.h declaration and recomp_overlays.inl record only)
python3 tools/rename_generated_symbols.py ... --start-address 0x80033630 --end-address 0x80033A00
renamed 0 references in 0 files
candidate 0x80033630 osSetIntMask: already-synchronized
rg -n -C 2 'osSetIntMask|osSetThreadPri|80033630|800336E0' .../symbol_files
libultra.txt:89 osSetIntMask = 0x80033630
libultra.txt:90 osSetThreadPri = 0x800336E0
```
