# M5 s4690: external retail-entry handoff

The single batched capture was run from `build/` with the whole-RDRAM oracle
control, exact voice span `0x1724C0..0x17250B`, adjacent control span
`0x17C000..0x17D000`, execution watches for `0x800903F0`, `0x80090C80`, and
`0x800921E8`, phase buckets for title `0x00790400/1024` and hangar
`0x006AB400/512`, writer histograms, post-store samples, and ordinal joins.
The port used one rebuilt binary with phase-attributed render-call rows.

## Evidence

- Retail whole-RDRAM control fired (`10000` callbacks), title had 632 VI
  samples, and hangar had 485 VI samples. The run completed 120 seconds.
- Retail exact-span phase histograms printed headers for both title and
  hangar but no writer rows. The full-run histogram did identify the named
  guest writers, including `0x800921E8` (93 writes) and `0x80007670` (76
  writes), but the retained post-store samples were outside the requested
  title/hangar buckets. The watched consumer `0x800903F0` had zero execution
  hits.
- Port title control fired and the run reached the title origin. It never
  reached the qualified hangar origin; its exact-span rows were all phase 3
  at `0x00696100` (76 rows), and its phase-attributed `0x800903F0` consumer
  had zero rows. The run then hit the known `musyxSynthFrame_s4562_impl`
  bus-error family.
- Port adjacent-range controls and the named writer arms fired, validating
  the port probes. The positive controls therefore make the requested
  title/hangar nulls interpretable.

## Result

This selects `H-route-absent` for the requested count-32 handoff phase. It
does not select a retail-entry writer or a port FE98/PI bridge corruption:
neither arm produced the target voice handoff followed by the watched
`0x800903F0` consumer in the qualified phase. No mitigation or pointer guard
is authorized. The external retail-entry thread is parked until a genuinely
new route discriminator is available.
