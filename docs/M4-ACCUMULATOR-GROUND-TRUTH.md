# M4 accumulator ground-truth measurement

Preparation result for the next M4 measurement. The retail oracle is an
independent CPU/RDRAM witness, not an RSP register witness: its write watches
can attribute RDRAM writers and its VI trace can prove phase reachability, but
the internal RSP `ACCH:ACCM:ACCL` tuple is not memory-mapped and cannot be
watched there.

## What the oracle can discriminate

The oracle run must carry both controls in the same invocation:

1. `--watch-write 0x0:0x800000` as the whole-RDRAM positive control. A zero
   whole-RDRAM count invalidates every targeted null.
2. A targeted watch covering the retail shaded-emitter input/output record
   addresses, selected only after the port-side probe identifies the stable
   physical range. `--vi-trace` (and the verified input schedule if needed)
   must show the corresponding shaded phase, not merely boot or attract.

The targeted result has three interpretations:

- A retail PC writes the candidate input/output record during the reached
  phase: the game owns that RDRAM edge, so a port-side mismatch cannot be
  assigned to an invented source without explaining the divergence.
- The whole-RDRAM control passes, the shaded phase is reached, and the
  targeted watch stays quiet: the candidate address/range is not a retail
  writer and the proposed source is rejected.
- The whole-RDRAM control passes but the shaded phase is not reached: the
  targeted null is unevaluable, not evidence for a runtime-only origin.

The oracle cannot select saturation versus ordinary arithmetic by itself. That
selection requires the port capture below, with the oracle serving as the
independent reachability and RDRAM-ownership line.

## Smallest complete paired capture

One future port build/run should emit, phase-gated to the first positive
`L_16B8` calls and with a bounded sample budget, one row containing:

`phase, task, ucode overlay, r9, v4[4], v0[4], ACCH[4], ACCM[4], ACCL[4],
v6_pre[4], v6_post_vmadh[4], v6_post_vge[4], output_record[0x18..0x4f]`.

The positive control is an independent non-M4 RSP arithmetic site in the same
run whose accumulator probe must fire with a nonzero or changing tuple. A
counter at `L_16B8` alone is not a control. The M4 row must be taken at the
exact final `VMADH v6,v4,v0`, before the following `VGE`, and again immediately
after it; the output record confirms the store destination and its resulting
bytes.

The comparison is deterministic:

- `v6_post_vmadh` matches the local VMADH model from the captured tuple, but
  `v6_post_vge`/stored bytes differ: VGE or store semantics remain open.
- The VMADH result already differs from the model: accumulator/product
  arithmetic or operand lanes are the active defect.
- The port tuple and store agree, while the oracle attributes a different
  retail record writer/input transition: source-state or execution divergence
  is active; do not add an RT64 mitigation.

No result is admissible without both the port positive-control row and an
oracle whole-RDRAM positive control. The oracle target range must be derived
from the same port capture; hard-coding an address before that capture would
make a null indistinguishable from watching the wrong record.
