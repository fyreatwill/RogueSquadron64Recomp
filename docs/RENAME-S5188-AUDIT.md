# Generated-symbol audit — `__osSiCreateAccessQueue`

Candidate: `__osSiCreateAccessQueue = 0x800338A0`.

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. Independent searches of the generated tree found no
body, placeholder, overlay record, or direct generated caller at the
companion address. The companion symbol map places `__osSiGetAccess =
0x800338F0` next, giving a nominal `0x50` span, but there is no generated body
or span to validate. This is an unmaterialized libultra/ABI entry rather than a
generated function available for semantic renaming.

Classification: preserve the existing ABI name; do not rename.

Evidence command:

```text
python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x800338A0 --end-address 0x80033A00
renamed 0 references in 0 files
candidate 0x80033960 sinf: already-synchronized
candidate 0x800338A0 __osSiCreateAccessQueue: already-synchronized
candidate 0x800338F0 __osSiGetAccess: already-synchronized
candidate 0x80033934 __osSiRelAccess: already-synchronized
```
