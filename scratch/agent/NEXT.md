# NEXT (s7829)
HYPOTHESIS-ID: g3-pose-port-input
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks this unit. G6c and all G5 items wait on the owner only.
Why: s7828 showed retail's steady lvl1 flight pose is timing-independent (CPO 2 vs 3: 0/42 sky vertices >=0.5 px) while the port
is pitched 0.0018-0.0020 rad (42/42). So a port-side input or computation differs. Bounded: at most 2 iterations, then close single-source.
Hypotheses:
 - H-stick: the guest reads a nonzero idle stick (main.cpp ~12755 get_n64_input has no host deadzone; a connected pad's drift reaches
   the game). Game dead zone is 0.015 after its x75/y80 scale (rs64_stick_gate.h comment), so drift of ~1 count could pass.
 - H-cpu-math: port float math in camera/attitude differs (s7825 audit found 0 fused mul-adds in game code, so less likely).
 - H-state: other initial state differs at mission start (save/RNG/controller-pak state).
Discriminator (ONE port run, the s7826 port half): add ROGUESQ_S7766_INLAT=1 (logs every guest pad read: btn, sx, sy) to the
s7826 port capture: `env SAVE_FROM=scratch/s6779/r1/lvl1.eep SECS=135 CAP0=12 AP=6:start,11:start,11.5:w1024,19.5:start,31.5:start,43.5:start,67.5:start,79.5:start,91.5:start,103.5:start
XE="ROGUESQ_AUTOPILOT_CLOCK=vi ROGUESQ_S7766_INLAT=1 RS64_RDP_BIN_PORT=$PWD/scratch/s7829/port.bin RS64_RDP_BIN_PORT_MAX_MB=6000" zsh tools/g3_port_capture.sh scratch/s7829/port`
Also note in the log whether SDL reports a game controller (stick-gate line / any controller open line).
Positive control: the [inlat] rows show btn bit START on the autopilot presses (proves the logger sees what the guest gets).
Outcomes: any sx/sy != 0 at rest in flight -> H-stick: rerun with ROGUESQ_STICK_GATE or a host deadzone / SDL controller disabled and
check the pose census vs retail (tools/s7827_tri_yshift_census.py scratch/s7828/cpo3L/retail.bin.zst P --win 2703:3300,<pf> --pose
2790:2990,<psteady> --pairs) -> pitch delta should vanish. sx=sy=0 throughout -> H-stick refuted: dump the camera matrix at the first
steady flight frame in port and oracle (oracle --debug-read on the camera struct) to name the diverging field (H-cpu-math vs H-state).
