# Session 5122 rename audit: `cosf`

Candidate: companion symbol `cosf = 0x8002B190`.

The generated snapshot contains the semantic `cosf_recomp` body at
`0x8002B190`. Its last generated instruction is at `0x8002B2FC`, giving an
exact `0x170`-byte span, matching the overlay record. There are 75 generated
call sites in `funcs_*.c`, independent of the body definition. The companion
map identifies the symbol as defined.

The bounded rename helper reported:

```text
renamed 0 references in 0 files
candidate 0x8002B190 cosf: already-synchronized
```

This selects the already-synchronized outcome. No source change, build, or
soak was warranted. Next candidate: `osCreateMesgQueue = 0x8002B300`.
