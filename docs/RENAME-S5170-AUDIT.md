# Generated-symbol audit — `__osPfsGetNextPage`

Candidate: `__osPfsGetNextPage = 0x80031AE0`

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. The companion symbol map places
`osPfsReadWriteFile = 0x80031BDC` next, giving a nominal `0xEC` span, but the
generated tree contains no function body or placeholder at `0x80031AE0`.
There is also no generated overlay record or direct generated caller for this
address. This is an unmaterialized libultra/ABI entry, so preserve the ABI
name; there is no body span to validate or rename.

Evidence commands and results:

```text
rg -n '__osPfsGetNextPage|func_80031AE0|fake_func_80031AE0' ...
(no matches)
python3 tools/rename_generated_symbols.py ... --start-address 0x80031AE0 --end-address 0x800327F0
renamed 0 references in 0 files
candidate 0x80031AE0 __osPfsGetNextPage: already-synchronized
rg -n '80031AE0|__osPfsGetNextPage|func_80031AE0|fake_func_80031AE0' ...
(no matches)
/Users/.../rogue_squadron64/symbol_files/libultra.txt:
__osPfsGetNextPage = 0x80031AE0; // defined:true
osPfsReadWriteFile = 0x80031BDC; // defined:true
```
