# NEXT: obtain a mission-capable retail handoff for the attached-mesh gap
HYPOTHESIS-ID: m3-attached-mesh-mission-route

The s4655 oracle capture qualified its whole-RDRAM control and reached
boot/title, but the attached-mesh handler was absent. Do not repeat that
route, add a NULL guard, or infer a global null. The next work unit is one
bounded route-driving attempt that reaches a mission/attachment phase, with
the same handler and `rs_free` execution watches plus the whole-RDRAM control.

Before any run, identify the exact verified input sequence or existing
savestate path that reaches a mission. Competing outcomes for that run are:

- handler plus `rs_free` caller rows: classify the two freed pointers and name
  the retail writer/legitimacy;
- handler rows but no matching `rs_free` caller: remap the action-2 call site;
- qualified controls but no handler: route remains unevaluable and this M3
  gap stays parked;
- absent controls: instrument invalid and redesign before conclusion.

The s4655 artifact is `scratch/agent/s4660_attached_mesh_oracle.log`.
