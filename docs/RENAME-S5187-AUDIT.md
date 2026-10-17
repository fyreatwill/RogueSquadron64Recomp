# Session 5187 symbol audit: `osSetTimer`

Candidate: `osSetTimer = 0x800337C0`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. Independent searches of the generated tree found no
body or placeholder at the companion address. The tree contains the ABI
declaration, a zero-size overlay record, and one generated call to the host
wrapper. The companion symbol map places `__osSiCreateAccessQueue` at
`0x800338A0`, giving a nominal `0xE0` span, but there is no generated body or
span to validate. This is an unmaterialized libultra/ABI entry rather than a
generated function available for semantic renaming.

Classification: preserve the existing ABI name; do not rename.
