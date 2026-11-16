# NEXT (s7470)
HYPOTHESIS-ID: host-asan-coverage

s7469 closed class DZ (hangar abort/re-entry under ASan: 3 re-entries, 4 mission loads, both plants PASS, 0 NEW groups).
Fold first: soak_queue/s7469_asan_w15_hold300.sh (exit 0 = PASS + 0 NEW; 1 = review NEW groups in scratch/s7469w/san_*;
3 = control FAIL). Record w15 initMission. If still 0 at HOLD=300, L15 dd8 21:9 does not reach flight under ASan on the quiet
harness: check its log for where it sits (title? level select?) before re-queuing, that is a route datum, not a sanitizer one.

Next unit (class EA): ASan per-level sweep. ASan flight so far covers L4, L7, L12 (dd4 16:9), L15/L16 (abort route). Sweep the
other 14 forced levels (0-3, 5, 6, 8-11, 13, 14, 17, 18) at the owner recipe on build_asan, 3 arms per soak recipe (the
s7468_asan_uc_routes layout: tools/g1e_owner_quiet_arms.zsh GAMEDIR=build_asan, HOLD=150, so() per arm), the FIRST arm of each
recipe carrying both plants (ROGUESQ_S7467_ASAN_PLANT=1 + ROGUESQ_S7468_UCODE_PLANT=1, --plant/--uplant <arm>). Alternate dd4 16:9
and dd8 21:9 arms. Write the 5 recipes in one go (s7470_asan_lv_a..e.sh, SOAK_NEEDS_IDLE=180, SOAK_TIMEOUT=900), queue them, and
if the host is idle run the first in-session. Score each with tools/s7467_san_report.py --known tools/s7467_san_reviewed.tsv and
log initMission per arm. Hypotheses: H-lv-clean (0 NEW groups in every arm that reached flight) / H-lv-hit (a NEW group named by
its stack: fix the writer, ORIGIN line) / H-lv-unreached (arm initMission=0: list it, re-queue with HOLD=300 once).
Close EA when every level has an arm with initMission>=1 and the plant arm passes in each recipe.
