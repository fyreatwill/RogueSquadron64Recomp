# Generated-symbol audit — `__osPfsRequestData`

Candidate: `__osPfsRequestData = 0x80031940`

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. The companion symbol map places
`__osPfsGetInitData = 0x80031A10` next, giving a nominal `0xD0` span, but the
generated tree contains no function body or placeholder at `0x80031940`.
There is also no generated overlay record or direct generated caller for this
address. This is an unmaterialized libultra/ABI entry, so preserve the ABI
name; there is no body span to validate or rename.

Evidence commands:

```text
rg -n '__osPfsRequestData|func_80031940|fake_func_80031940' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x80031940 --end-address 0x80031A10
rg -n -C 3 'osPfsRequestData|80031940|80031A10' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```
