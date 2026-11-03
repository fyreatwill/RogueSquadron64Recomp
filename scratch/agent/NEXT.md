# NEXT: G1e FPS60 hangar per-tick sites - find the hangar frame dt, scale the hangar ship spin
HYPOTHESIS-ID: g1e-fps60-hangar-quanta

Context: s6828 closed the mission float-quanta class. Left: hangarVehicleDisplayNpcHandler (0x800C68A0) ship-spin velocity
+0x8 / +0xC: += stick*const (0x800C6BD0, 0x800C6C34) and decay -= const (0x800C6CBC / 0x800C6CD4, 0x800C6D0C ...) per call,
clamped. At FPS60 the hangar updates 60/s (s6791), so spin-up/settle is 2x faster. The angle integration of +0x8/+0xC (who
reads them: grep the function and setObject*Rotation callers) may be per-tick too - include it.
Hypotheses: H-dt-exists (the hangar loop has a dt global, e.g. the one the s6791 camera curve uses - find setupCameraMatrices'
or the hangar camera's time source, ROGUESQ_G3F_CAM recipe scratch/s6791), H-no-dt (hangar is frame-counted: then derive k
from the FPS60 lever state 0x80128EAF == 1 -> k = 0.5).
Step 1 offline: find the hangar dt source (grep the hangar camera 0x800CD670 path for a dt load; compare with 0x80130BA4).
Step 2: extend tools/fixup_fps60_float_quanta.py (same switch) for the spin add/decay/integration sites; capture the hangar k.
Verify, one build: hangar route (scratch/s6791 recipe), hold stick right 2 s then release, arms a30 / FPS60 fix / FPS60
FQUANTA=0; trace +0x8 per call (add the pcs to fixup_fps60_float_trace.py) -> spin vs real time must match a30 in the fix arm.
Done = hangar spin rate-independent or classified retail-acceptable with numbers; then take the ladder's next rung (G3 in-flight
frame diffs vs retail or G5).
