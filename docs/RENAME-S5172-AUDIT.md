# Session 5172 symbol audit: `osPfsRepairId`

Candidate: `osPfsRepairId = 0x80032000`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. The generated tree has no function body, placeholder,
or overlay record at the companion address; its only generated-tree reference
is the ABI call from `funcs_2.c`. The companion symbol map places the next
entry, `osPfsFindFile`, at `0x80032260`, so there is no generated span to
validate. This is an unmaterialized libultra/ABI entry rather than a generated
function available for semantic renaming.

Classification: preserve the existing ABI name; do not rename.
