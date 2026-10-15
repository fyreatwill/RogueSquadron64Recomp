# Next work unit: classify the 8 port 640-phase task-end accl==0x8000 lanes (vs retail 0/425)

HYPOTHESIS-ID: m4-accumulator-origin-new-witness

s5005 closed the hangar end-of-task accumulator (port 0/1955, retail 0/576). Residual: port phase ord 3 (640) has 8/1281
tasks with an accl 0x8000 lane; retail 640 has 0/425. Offline: rerun scratch/agent/s5005_port_end_acc.sh, list the
[m4-end] sat8000>0 rows (task, lane, acch.accm.accl) and check whether the 48-bit value is a clamp artifact (accm/acch
saturation pattern) or an ordinary product. Outcomes: clamp-shaped => genuine port-vs-retail ucode divergence in the 640
phase (name the op); ordinary => close the thread, then return to M5 de-stub (docs/M5-AUDIO-PLAN.md) or an M3 idiom audit.
Positive control: same-run nz>0 rows. Do not rewrite any value.
