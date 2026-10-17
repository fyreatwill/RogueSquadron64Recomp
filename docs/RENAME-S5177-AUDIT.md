# Session 5177 symbol audit: `osCartRomInit`

Candidate: `osCartRomInit = 0x800326F0`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. Independent searches of the generated tree found no
function body or placeholder at the companion address. The generated tree has
only the ABI declaration and a zero-size overlay record at offset `0x322B0`,
with no direct generated callers, which is consistent with an unmaterialized
host wrapper or ABI entry. The companion symbol map places `osGetThreadPri` at
`0x80032FB0`, giving a nominal `0x8C0` span, but there is no body to validate.

Classification: preserve the existing ABI name; do not rename.
