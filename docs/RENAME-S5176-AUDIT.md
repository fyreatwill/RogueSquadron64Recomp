# Session 5176 symbol audit: `osCreatePiManager`

Candidate: `osCreatePiManager = 0x80032560`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. Independent searches of the generated tree found no
function body or placeholder at the companion address. The generated tree has
one direct caller and a zero-size overlay record at offset `0x32120`, which is
consistent with a host wrapper or ABI declaration rather than materialized
generated code. The companion symbol map places `osCartRomInit` at
`0x800326F0`, giving a nominal `0x190` span, but there is no body to validate.

Classification: preserve the existing ABI name; do not rename.
