# Generated-symbol audit — `__osSiRawWriteIo`

Candidate: `__osSiRawWriteIo = 0x80033C50`

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. Independent generated-tree searches found no
function body, placeholder, overlay record, or direct generated caller at
the companion address. The symbol map places `proutSprintf = 0x80033CA0`
next, giving a nominal `0x50` span, but there is no body span to validate.
This is an unmaterialized libultra/ABI entry, so preserve the ABI name.

Evidence commands and results:

```text
rg -n '__osSiRawWriteIo|func_80033C50|fake_func_80033C50' ...
(no matches)
python3 tools/rename_generated_symbols.py ... --start-address 0x80033C50 --end-address 0x80033CA0
renamed 0 references in 0 files
candidate 0x80033C50 __osSiRawWriteIo: already-synchronized
rg -n '80033C50|80033CA0|__osSiRawWriteIo|__osSiRawReadIo|osSiRaw' ...
only the companion symbol-map entries were present
```
