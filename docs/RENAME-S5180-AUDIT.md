# Session 5180 symbol audit: `osPiRawReadIo`

Candidate: `osPiRawReadIo = 0x80033170`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. The bounded generated-tree search found no function
body, placeholder, overlay record, or direct generated caller at the
companion address. The next companion symbol-map entry is
`osRecvMesg = 0x800331D0`, giving a nominal `0x160` span, but there is no body
to validate.

Classification: preserve the existing ABI name; do not rename.
