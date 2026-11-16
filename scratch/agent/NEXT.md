# NEXT (s7468)
HYPOTHESIS-ID: host-asan-coverage

s7467 closed class DW: ASan+UBSan owner-recipe flight (L4/L12 dd4 16:9), control PASS, 1 real UBSan defect fixed (plume Metal
uninit depth bias), 12 FP groups in tools/s7467_san_reviewed.tsv (KNOWN rows). Queued: soak_queue/s7467_asan_routes.sh
(p plant + L7 dd4 + L15 dd8 21:9). Fold its verdict first: exit 0 = 0 NEW groups; 1 = review each NEW group in
scratch/s7467r/san_* (classify REAL/FP, fix REAL with ORIGIN, add KNOWN row); 3 = control FAIL (instrument blind).

Next unit (class DY): the RSP ucode TUs are the one host C++ not instrumented in build_asan (CMakeLists s7467 exemption).
They index DMEM/IMEM host arrays with guest-derived addresses (s5597's poke_be32 overflow lived next to them). Hypotheses:
H-ucode-clean (ASan over the ucode TUs reports 0 outside the plant) vs H-ucode-hit (an out-of-array DMEM/IMEM/stack access,
named by its stack) vs H-ucode-slow (ucode ASan too slow to reach flight: initMission=0 in 150 s; then use
ROGUESQ_AUTOPILOT_CLOCK=frames or a longer HOLD). Discriminator: a second dir (build_asan_uc: copy tools/build_asan.sh with
-DROGUESQ_ASAN_UCODE=ON and B=build_asan_uc, or add a UCODE=1 switch to build_asan.sh), one run of the s7467 recipe
(scratch/s7467/asan_flight.sh with GAMEDIR=build_asan_uc), score with tools/s7467_san_report.py --plant p --known
tools/s7467_san_reviewed.tsv. Add a ucode-side plant if the boot plant is not enough to prove the ucode TU is instrumented
(e.g. nm build_asan_uc objects for __asan_report in the ucode .o files = build-level check, then a runtime plant).
