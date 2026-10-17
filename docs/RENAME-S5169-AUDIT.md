# Generated-symbol audit — `__osPfsGetInitData`

Candidate: `__osPfsGetInitData = 0x80031A10`

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. The companion symbol map places
`__osPfsGetNextPage = 0x80031AE0` next, giving a nominal `0xD0` span, but the
generated tree contains no function body or placeholder at `0x80031A10`.
There is also no generated overlay record or direct generated caller for this
address. This is an unmaterialized libultra/ABI entry, so preserve the ABI
name; there is no body span to validate or rename.

Evidence commands and results:

```text
rg -n '__osPfsGetInitData|func_80031A10|fake_func_80031A10' ...
(no matches)
python3 tools/rename_generated_symbols.py ... --start-address 0x80031A10 --end-address 0x80031AE0
renamed 0 references in 0 files
candidate 0x80031A10 __osPfsGetInitData: already-synchronized
rg -n '80031A10|__osPfsGetInitData|func_80031A10|fake_func_80031A10' ...
/Users/.../rogue_squadron64/symbol_files/libultra.txt:154:__osPfsGetInitData = 0x80031A10; // defined:true
```
