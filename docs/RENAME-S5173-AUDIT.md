# Session 5173 symbol audit: `osPfsFindFile`

Candidate: `osPfsFindFile = 0x80032260`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. The generated tree has the ABI declaration, two
generated call sites, and a zero-size overlay record at offset `0x31E20`, but
no generated body or placeholder at the companion address. The companion
symbol map places the next entry, `osPiStartDma`, at `0x80032420`, giving a
nominal span of `0x1C0`; without a generated body there is no span to
validate. This is an unmaterialized libultra/ABI entry rather than a generated
function available for semantic renaming.

Classification: preserve the existing ABI name; do not rename.
