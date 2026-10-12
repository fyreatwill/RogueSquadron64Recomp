# NEXT: classify hangar shade-LSB drift, or renderer-side triage
HYPOTHESIS-ID: m4-vge-store-boundary-ground-truth

RESUME: s4633 re-ran the aligned RDP diff (port frame 771 vs retail frame 0): edge/z/tex/state
equal; 109/1249 tris differ only in shade words by +-1 LSB-ish (s4520 had 3).
Hypotheses: H-anim (lighting term animates, alignment drift), H-round (RSP rounding in
VMUDN/VMACF/pack differs), H-render (artifacts are renderer-side, stream is fine).
Discriminator: capture 3 port runs and compare port-vs-port frame 771 shade words (if the
109 vary run to run it is animation; if identical it is deterministic rounding); positive
control: tris 850-1246 known differ. Then if deterministic, unit-test VMUDN/VMADN/VMACF
rounding vs ares on those operands. Scripts: scratch/agent/s4633_port_rdp.sh,
s4518_shade_cmp.py, s4633_shade_detail.py.
