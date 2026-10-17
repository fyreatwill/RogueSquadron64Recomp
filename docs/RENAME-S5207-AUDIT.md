# Session 5207 symbol audit: `osStartThread`

Candidate: `osStartThread = 0x800344E0`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. Independent searches of the generated functions,
header, and overlay records found no generated body or placeholder at the
companion address. The generated tree contains the ABI declaration, a
zero-size overlay record, and 12 calls to the existing host wrapper. The
companion symbol map places `osStopThread = 0x80034630` next, giving a nominal
`0x150` span, but there is no body to validate.

Classification: unmaterialized libultra/ABI entry; preserve the existing
semantic name and do not rename. No build or soak was warranted for this
naming-only result.
