# NEXT: G3b in-flight spike lines (owner report 2026-10-24)
HYPOTHESIS-ID: g3b-spike-lines
G4 crash hunting is PARKED by the owner; the queued s6081/s6082 G4 soaks were moved to
soak_queue/cancelled/. Ignore any G4 result still landing (a run in progress may finish).
Take ITERATION.md item 3c G3b: build the one-build spike-triangle instrument (RDP tris
with any vertex beyond a 2x-viewport guard band or w~0, with frame number, coords and
source task, plus framebuffer dumps on those frames), queue a 300 s lvl2 hold, and
confirm the positive control (count > 0 on a frame with a visible flash) before
discriminating H-rsp / H-rt64 / H-retail.
