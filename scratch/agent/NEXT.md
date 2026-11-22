# NEXT (s7834)
HYPOTHESIS-ID: g3-flight-pitch-cpu-state
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks this unit. G6c and all G5 items wait on the owner only.
Why: s7833 refuted H-rate. Retail's lvl2 flight camera pose is the same at 471/794/969 game frames (CountPerOp 3/2/1), and the port
(957 frames) is pitched ~+0.002 rad vs all of them. So a port-side state difference independent of frame rate. Sub-pixel, not
owner-visible: this is the LAST unit on the thread. If it does not name a first-divergent field, close single-source.
Hypotheses:
 - H-craft: the craft's own pitch/attitude (flight model state) differs, and the camera follows it faithfully.
 - H-cam: craft attitude equal, camera rig differs (camera pitch offset/lag/target height computed differently).
 - H-proj: camera block equal, the difference enters at matrix build (setupCameraMatrices; s7825 FMA/FCSR audit found IEEE-identical
   ops, so a different input is likelier than a different op).
Discriminator: ONE dump per side of the camera block (*0x80138D1C is the camera pointer used by radfade/edgepos, s7xxx; the
s6875 "camera block" comparison is prior art, grep PORTING-STATE 181333) and the player craft's attitude floats, per game frame,
over the flight bands. Port: an env-gated per-frame RAM dump (existing hook or a small fixup-script diagnostic, NOT a hand-edit to
generated code). Retail: rs64_oracle memory read of the same physical range (see tools/oracle/README.md; --watch-write on the
camera block gives value + PC per write; positive control: whole-RDRAM watch). Route = s7832 lvl2 (EEP=scratch/s7832/lvl.eep, PP as
s7833, CPO=2) and the s7832 port recipe. Align frames by the tri-count band sequence (bands a/b, s7833 tool).
Outcomes: craft attitude differs -> H-craft (record which field first diverges and when; stop). Craft equal, camera block differs ->
H-cam. Both equal -> H-proj. Close the thread with that answer either way; no further iterations.
