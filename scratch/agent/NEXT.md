# Next work unit: render-fidelity A/B of the mission origin framebuffer (port vs retail oracle)
HYPOTHESIS-ID: render-fidelity-mission-fb-phase-gated
Backlog of audit threads (M3/M4/M5/indirect sites) is exhausted; do NOT redo the indirect-site audit
(s4821/s4998/s5357). New milestone (human option (a)): render fidelity at the first mission origin
(VI 512, 0x00690400 / 0x00620400), the one area never compared against retail.
Method: reach the phase with the validated autopilot route (3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a)
in BOTH the port and the rs64-oracle (cxd4 + an attached video plugin, see oracle --help `--video PATH`), phase-gate
on the VI transition (no cross-run A/B on animating frames), dump the framebuffer once from each, diff offline.
Positive control: same-run dump of the title screen (VI 1024) must match within tolerance first.
A null result without that control is not a result. One game run at a time.
Open dependency (not blocking): MIPS cross-toolchain for fresh PatchesLib qualification (clang has no MIPS target, verified s5390).
