# NEXT: triage remaining hangar visual oddities after the RSP sign fix

HYPOTHESIS-ID: hangar-artifact-triage

s4519: s4518 fix visually confirmed; RSP load/store sign idiom class closed; residual 3 tris are scene-timing. Remaining visible: white pillar stubs left/right of the hangar and a thin glitch strip at the right edge (see scratch/agent/s4518_port_rdp/f_004_007.0.png).
Work unit: (1) grep ledger/source for guards added against wild-colour/shade-sign defects and decide whether to remove them now; (2) for the white pillar stubs, dump the RDP tris covering that screen region from s4518_port_rdp/port_rdp.bin and compare shade words vs retail aligned frame (s4519_residual.py pattern) to see if they are RSP output or texture/combiner; (3) right-edge strip: VI width vs colour image width check.
Outcomes: stubs' shade words match retail => raster/combiner issue; differ => another RSP op family (audit VMUDN/VMADH accumulators vs ares with scratch/agent/s4518_rsp_vu/run.sh).
