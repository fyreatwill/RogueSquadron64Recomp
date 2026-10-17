# Session 5202 symbol audit: `__osSpRawStartDma`

Candidate: `__osSpRawStartDma = 0x80034350`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. Independent searches of the generated functions,
header, and overlay records found no generated body, placeholder, overlay
record, or direct generated caller at the companion address. The companion
symbol map places `__osSpSetPc = 0x800343E0` next, but there is no body to
validate across that `0x90` span.

Classification: unmaterialized libultra/ABI entry; preserve the existing
semantic name and do not rename. No build or soak was warranted for this
naming-only result.
