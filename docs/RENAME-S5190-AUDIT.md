# Session 5190 — `__osSiRelAccess` audit

Candidate: `__osSiRelAccess = 0x80033934`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. Independent searches of the generated tree found no
body, placeholder, overlay record, or direct generated caller at the
companion address. The symbol map places `__osSiRawStartDma = 0x80033B20`
next, giving a nominal `0x1EC` span, but there is no generated body to
validate. Preserve the existing ABI name.

The helper also surfaced `sinf = 0x80033960` as already synchronized; it is a
separate libultra symbol and does not provide a generated body for
`__osSiRelAccess`.
