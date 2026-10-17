# Session 5174 symbol audit: `osPiStartDma`

Candidate: `osPiStartDma = 0x80032420`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. The generated tree has the ABI declaration, four
generated call sites, and a zero-size overlay record at offset `0x31FE0`, but
no generated body or placeholder at the companion address. The companion
symbol map places the next entry, `osPiGetCmdQueue`, at `0x80032530`, giving a
nominal span of `0x110`; without a generated body there is no span to
validate. This is an unmaterialized libultra/ABI entry rather than a generated
function available for semantic renaming.

Classification: preserve the existing ABI name; do not rename.
