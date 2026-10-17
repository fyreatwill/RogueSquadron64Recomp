# Session 5200 symbol audit: `bcopy`

Candidate: `bcopy = 0x80034010`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. The generated tree contains a complete
`bcopy_recomp` body beginning at `0x80034010` and ending at the delay-slot
instructions through `0x8003431C`. The companion symbol map places
`__osSpDeviceBusy = 0x80034320` next, so the body exactly fills the `0x310`
span. One independent generated caller invokes `bcopy_recomp`.

Classification: already correctly named libultra/ABI entry; preserve the
semantic name and do not rename. No build or soak was warranted for this
naming-only result.
