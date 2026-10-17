# Session 5182 symbol audit: `osSendMesg`

Candidate: `osSendMesg = 0x80033410`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. The generated tree contains the ABI declaration and
a zero-size overlay record at offset `0x32FD0`, but no generated body or
placeholder at the companion address. There are 44 generated call sites to
the host wrapper. The next companion symbol-map entry is
`osSetEventMesg = 0x80033560`, giving a nominal `0x150` span, but there is no
body to validate.

Classification: preserve the existing ABI name; do not rename.
