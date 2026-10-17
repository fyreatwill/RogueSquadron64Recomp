# Generated-symbol audit — `osPfsIsPlug`

Candidate: `osPfsIsPlug = 0x800317A0`

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. The companion symbol map places
`__osPfsRequestData = 0x80031940` next, giving a nominal `0x1A0` span, but the
generated tree contains no function body or placeholder at `0x800317A0`.
There is also no generated overlay record or direct generated caller for this
address. This is an unmaterialized libultra/ABI entry, so preserve the ABI
name; there is no body span to validate or rename.

Evidence commands:

```text
rg -n 'osPfsIsPlug|func_800317A0|fake_func_800317A0' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x800317A0 --end-address 0x80031BDC
rg -n -C 3 'osPfsIsPlug|800317A0|80031940' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```
