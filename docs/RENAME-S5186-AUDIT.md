# Generated-symbol audit — `osSetThreadPri`

Candidate: `osSetThreadPri = 0x800336E0`

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. The companion symbol map places
`osSetTimer = 0x800337C0` next, giving a nominal `0xE0` span, but the
generated tree contains no function body or placeholder at `0x800336E0`.
It contains only the ABI declaration in `funcs.h`, a zero-size overlay
record, and two direct generated callers of the host wrapper. This is an
unmaterialized libultra/ABI entry, so preserve the ABI name; there is no body
span to validate or rename.

Evidence commands and results:

```text
rg -n 'osSetThreadPri|func_800336E0|fake_func_800336E0' ...
(funcs.h declaration, recomp_overlays.inl record, and two generated callers)
python3 tools/rename_generated_symbols.py ... --start-address 0x800336E0 --end-address 0x80033A00
renamed 0 references in 0 files
candidate 0x800336E0 osSetThreadPri: already-synchronized
candidate 0x800337C0 osSetTimer: already-synchronized
```
