# NEXT (s7815)
HYPOTHESIS-ID: rsp-vu-elementwise-vs-cxd4
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
Why: s7814's per-helper map of the LLE ucode C (tools/s7814_include_census.py) shows every helper evidenced, but the 31 elementwise
VU ops the ucode compiles (VMADN 554, VMADH 504, VMADM 318, VMUDL 283, VMUDN 204, VSUB/VSUBC 162, VADD 115, VMUDM 118, VGE 84, VMRG 88,
VMUDH 68, VADDC 62, VABS 50, VLT 44, VXOR 36, VCH/VCL 20, VCR 10, VAND 18, VMULF 15, VMADL 24, VEQ 4, VNE 2, VNXOR 2) rest on
ares SIMD-vs-SISD (s6301: two code paths of ONE emulator) plus cxd4 whole-task replays (s7751, a few captured tasks). No op-level
independent reference. G3c(b) asked for exactly this (VMULF/VMACF rounding, VCH/VCL/VCR flags vs cxd4/parallel-rsp).
Unit: extend the s7814_vmov_vsar pattern (tools/s7814_vmov_vsar/run.sh + harness.cpp: live headers copied each run, cxd4 bodies
extracted verbatim from ../rs64-oracle/src/mupen64plus-rsp-cxd4/vu/{multiply,add,select,logical}.c, element broadcast written from
the RSP manual, WHOLE vpu struct compared incl. VCO/VCC/VCE and all 3 acc slices) to every op above, every e 0..15, random + edge
inputs (0, 1, 0x7FFF, 0x8000, 0xFFFF, acc near clamp boundaries), vd==vs/vt aliasing. cxd4 keeps flags in cf_* arrays and acc in
VACC[3][8]: map both ways (see to_ref/from_ref). Run the gfx-TU flavour too (-DRS64_RSP_NEON_MAC=1, as the shipped gfx TU builds).
Hypotheses: H-equal (0 diffs: ares == cxd4 on every live op) / H-differ-dead (diffs only on ops/e/flag states the ucode never
reaches: prove with the s7509 operand table + a reachability argument) / H-differ-live (a live op differs -> decide which emulator
matches hardware with a third source (parallel-rsp or n64brew/RSP docs), fix ours, re-run s7751 whole-task replay as the end-to-end).
Controls: one mutant per op family (multiply clamp, add carry VCO, compare VCC, clip VCE, merge select) must fire.
CPU rule: harness only, no game run; keep reps so the whole run is < 2 min.
