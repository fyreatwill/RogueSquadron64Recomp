# Generated-symbol audit — `osPfsInitPak`

Candidate: `osPfsInitPak = 0x80030AA0`

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. The companion symbol map places
`osPfsChecker = 0x80030D40` next, giving a nominal `0x2A0` span, but the
generated tree contains no function body or placeholder at `0x80030AA0`.
`recomp_overlays.inl` contains only the zero-size host-wrapper record
`osPfsInitPak_recomp` at ROM offset `0x30660`, and `funcs_2.c` has one direct
generated caller at `0x800059DC`. There is therefore no generated body span
to validate or rename; preserve the ABI name.

Evidence commands:

```text
rg -n 'osPfsInitPak|func_80030AA0|fake_func_80030AA0' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x80030AA0 --end-address 0x80030D40
```
