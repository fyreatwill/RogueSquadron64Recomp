# Session 5130 rename audit

Candidate: `__osException = 0x8002B600`.

The bounded helper was run over `0x8002B600..0x8002BF00` with the companion
symbol files. It changed zero references and reported
`__osException: already-synchronized`. The generated snapshot contains no
`func_8002B600`, `fake_func_8002B600`, or `__osException` body/reference in
`funcs_*.c`, `funcs.h`, or `recomp_overlays.inl`. The companion map places the
next named entry at `__osEnqueueAndYield = 0x8002BC1C`, but there is no
generated overlay record at the candidate address and no direct generated
caller to count.

Classification: host-wrapper/ABI boundary or unmaterialized exception entry;
preserve the existing ABI naming and do not build or soak. This is an
independent companion-map/helper result plus a generated-tree search; no
semantic rename is justified.
