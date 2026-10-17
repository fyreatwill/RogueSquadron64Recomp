# Session 5179 symbol audit: `osPiRawStartDma`

Candidate: `osPiRawStartDma = 0x80033090`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. Independent searches of the generated tree found no
function body, placeholder, overlay record, or direct generated caller at the
companion address. The next companion symbol map entry is
`osPiRawReadIo = 0x80033170`, giving a nominal `0xE0` span, but there is no
body to validate.

Classification: preserve the existing ABI name; do not rename.
