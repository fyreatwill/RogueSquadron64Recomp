# M5 s3414 — retail producer destination map

The corrected independent-oracle run used the driven Rice route, the whole-
RDRAM positive control, producer execution watch `0x800078EC`, both candidate
physical destinations, post-store sampling, and the explicit hangar bucket
`origin=0x006AB400:512`.

Results:

- The positive control reached 11,866 writes and the run reached 7,173 VI
  frames.
- The hangar bucket contained 1,540 VI rows.
- The producer wrote `0x1797B0:0x179A48` 664 times in the hangar bucket, all
  attributed to `0x800078EC`.
- The producer wrote no bytes in `0x1935E0:0x1935F0` in the hangar bucket;
  the 36 writes there were attributed to other PCs.
- Producer post-store samples for the source span were 1,328 total, with 340
  nonzero samples. The alternate destination had 16 producer samples, 6
  nonzero, but none in the hangar writer histogram.
- The producer executed 3,245,475 times overall; its predecessor histogram
  included `0x8002BEEC` for 180 executions.

This selects `H-RetailPublishes1797B0`: retail does publish nonzero payload in
the same physical source span used by the port. It refutes a retail-only
destination mismatch at `0x1935E0` for the observed hangar producer edge. The
remaining gap is port-side producer input/payload formation; no runtime or
audio behavior was changed. Raw capture:
`scratch/agent/s3414_retail_destination_map_final/oracle.log`.
