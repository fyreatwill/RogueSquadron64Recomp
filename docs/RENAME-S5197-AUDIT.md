# Session 5197 symbol audit: `_VirtualToPhysicalTask`

Candidate: `_VirtualToPhysicalTask = 0x80033D20`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. The generated tree contains a body beginning at
`0x80033D20`; its final instruction is at `0x80033E38`, so it ends at
`0x80033E3C`. This exactly matches the companion symbol-map span of `0x11C`
to the next entry, `osSpTaskLoad = 0x80033E3C`, and the overlay record at
offset `0x338E0`. The generated tree has no independent caller beyond the
definition/declaration and overlay record.

Classification: already correctly named; preserve the ABI-semantic name and
do not rename.
