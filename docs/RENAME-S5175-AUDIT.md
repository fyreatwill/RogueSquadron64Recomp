# Session 5175 symbol audit: `osPiGetCmdQueue`

Candidate: `osPiGetCmdQueue = 0x80032530`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. Independent searches of the generated tree found no
body, placeholder, or overlay record at the companion address. The companion
symbol map places `osCreatePiManager` at `0x80032560`, giving a nominal `0x30`
span, but there is no generated body or span to validate. This is an
unmaterialized libultra/ABI entry rather than a generated function available
for semantic renaming.

Classification: preserve the existing ABI name; do not rename.
