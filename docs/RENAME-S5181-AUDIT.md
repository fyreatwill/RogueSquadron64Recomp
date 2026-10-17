# Session 5181 symbol audit: `osRecvMesg`

Candidate: `osRecvMesg = 0x800331D0`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. The generated tree contains the ABI declaration and
a zero-size overlay record at offset `0x32D90`, but no generated body,
placeholder, or direct generated caller at the companion address. The next
companion symbol-map entry is `osSendMesg = 0x80033410`, giving a nominal
`0x240` span, but there is no body to validate.

Classification: preserve the existing ABI name; do not rename.
