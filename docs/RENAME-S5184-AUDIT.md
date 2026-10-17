# Session 5184 symbol audit: `osSetEventMesg`

Candidate: `osSetEventMesg = 0x80033560`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. The generated tree contains the ABI declaration and
a zero-size overlay record at offset `0x33120`, but no generated body or
placeholder at the companion address. There are five generated call sites to
the host wrapper. The next companion symbol-map entry is
`osSetIntMask = 0x80033630`, giving a nominal `0xD0` span, but there is no
body to validate.

Classification: preserve the existing ABI name; do not rename.
