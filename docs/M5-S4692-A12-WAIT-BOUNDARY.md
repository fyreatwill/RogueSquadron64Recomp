# M5 A12 wait boundary — session 4692

The rebuilt qualified real-audio/LLE route reached title and hangar controls
(2,421 and 208 phase rows). `waitForMusyXAudioTaskDone` entered five times.
Its default yielding arm observed countdown 16, then returned after countdown
0 five times; no pump cap, spin timeout, crash, or abort occurred. The
separate `0x8014974C` diagnostic saw flag 0 on entry, so its unbounded
nonzero spin was not reached in this phase.

The independent retail oracle passed the whole-RDRAM control (477,344 hits),
reached title 1024 and hangar 512, and showed the four candidate
`musyxSynthFrame` writer PCs executing in the target phases:
`0x80091480` (10,330), `0x80091540` (1,090), `0x800915F4` (347), and
`0x800916A4` (13,274). The retail flag range `0x14974C` was written 24,219
times and the adjacent `0x149800..0x149A00` control range 425,205 times.
The exact countdown watch `0x14998A..0x14998C` was zero-hit, while the
adjacent writer rows placed `0x800916A4` at `0x149988`; retail therefore
establishes writer activity and the adjacent state family, but not an exact
retail write to the port's `0x14998A` field.

This selects H-A12-countdown-writer-valid for the covered port route, with
the exact retail field mapping explicitly unresolved. It also closes the
separate-flag spin as a blocker for this route. No wait, spin, or state change
is authorized. Artifact: `scratch/agent/s4692_m5_a12_wait_boundary/`.
