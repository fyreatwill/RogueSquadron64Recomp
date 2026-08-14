# Factor 5 shade accumulator audit

Static audit of the generated `L_16B8` shade path and the local RSP
accumulator implementation. No generated code was changed.

## Instruction order

The relevant sequence is:

```
vmudl v5, v20, v26[3h]
vmadm v5, v21, v26[3h]
vmadn v5, v20, v6[3h]
vmadh v4, v21, v6[3h]
vmudl v5, v5,  v19[0]
vmadm v4, v4,  v19[0]
vmadn v5, v30, v30[0]
vmudh v7, v1,  v30[1]
vmadn v7, v5,  v0
vmadh v6, v4,  v0
vge   v6, v6,  v29[1q]
```

The accumulator is shared by lanes and is not attached to the destination
register. The accumulator entering the final `vmadh v6,v4,v0` was therefore
most recently updated by `vmadn v7,v5,v0`, not by the preceding `vmadm v4`.
The final VMADH adds the signed `v4*v0` product into that shared state and
writes the high/middle slice to `v6`.

## Saturation rule

The local SISD model is equivalent to:

```
result = signed_high_32(accumulator) + signed(v4) * signed(v0)
ACCH:ACCM = result
v6 = signed-saturate(ACCH:ACCM, slice=middle)
```

Its saturation helper returns `0x8000` when the accumulator is negative and
outside the representable signed range, or when `ACCH=0xffff` and `ACCM` is
nonnegative. It returns ordinary `ACCM` when the high and middle words are a
valid sign extension. An observed `0x8000` lane is therefore compatible with
negative saturation, but static instruction shape alone cannot distinguish that
from an in-range middle word of `0x8000` with a sign-extending high word.

The DMEM-0x60 `v29` vector is `0577 638F 1756 FF96 04D1 62CB 18CB FF8A`;
no lane is `0x8000`. The final VGE cannot select the observed sentinel from
`v29`.

## Verdict

`H-v29-selection` is refuted by the independent table bytes and local VGE
select semantics. The saturation-vs-ordinary-arithmetic discriminator is not
complete: no capture contains the per-lane `ACCH:ACCM:ACCL`, `v4`, and `v0`
values at this exact VMADH. The next measurement must capture that complete
pre/post tuple in one phase-gated run, with an independent positive-control RSP
operation, before selecting between the remaining two hypotheses.
