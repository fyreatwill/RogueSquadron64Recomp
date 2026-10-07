# M5 s4158 pre-clear writer mismatch

The s4157 census was rerun with the same rebuilt binary and the fixed
phase-gated route. The port reached VI 1024 at 13.4s and VI 512 at 24.5s;
`m5-preclear-writer-control` fired in both target phases. This is a valid
positive control, so the earlier port route-invalid result is not carried
forward.

The port target-span parity rows were zero-valued: `0x80007670` wrote zero in
the earlier 640 phase and `0x800078EC` wrote zero in hangar. No nonzero port
writer matching the retail source was observed. The independent retail arm
passed whole-RDRAM/title/hangar controls, recorded 1,830 writes to
`0x1797B0..0x179A48`, and its hangar snapshot contained nonzero bytes; its
writer set included `0x80007670`, `0x800078EC`, `0x8001E2C0`, and the
`0x8001FAxx` family.

Selection: H-earlier-writer-mismatch. The port writer instrument is live and
the route is target-valid, but its observed target-span values do not match
the retail nonzero source. This does not identify whether the port writer is
fed the wrong object, whether a retail writer is absent from the port route,
or whether the current parity rows under-sample the span.

ORIGIN: the guest target-span writers, with retail nonzero values legitimate
and the port zero values observed rather than suppressed; no guest, audio,
wait, cap, predicate, slot, or writeback behavior changed.
