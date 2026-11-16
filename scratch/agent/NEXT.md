# NEXT (s7469)
HYPOTHESIS-ID: host-asan-coverage

s7468 closed class DY (ucode TUs under ASan, both controls PASS, 0 new groups, flight reached). build_asan is now UCODE=1 (default).
Fold first: soak_queue/s7468_asan_uc_routes.sh verdict (exit 0 = 0 NEW groups; 1 = review NEW groups in scratch/s7468r/san_*;
3 = a control FAIL). If w15 again shows initMission=0, the L15 dd8 21:9 flight stays uncovered: note it, and give it a longer
HOLD (300) in a follow-up soak instead of re-running 150.

Next unit (class DZ): ASan coverage of the routes the forced-level recipe never takes: the owner hangar route with abort and
re-entry (title -> SELECT YOUR CRAFT -> mission -> PAUSE/ABORT -> hangar -> mission again), driven by scratch/s7326/run.zsh
(owner save read-only; check it can run from GAMEDIR=build_asan or add that override). These paths free and rebuild the mission
and hangar objects, which is where host use-after-free/stale-pointer bugs would show (G5i re-entry state, endMissionCleanup re-init).
Hypotheses: H-route-clean (0 NEW groups over >=2 abort/re-entry cycles) vs H-route-hit (a NEW ASan group, named by stack: fix
the writer, ORIGIN line) vs H-route-unreached (ASan too slow for the key-timed route: then phase-gate keys on VI, not time).
Positive control in the same run: ROGUESQ_S7467_ASAN_PLANT=1 + ROGUESQ_S7468_UCODE_PLANT=1 on the first boot; score with
tools/s7467_san_report.py <R> <arms> --plant <arm> --uplant <arm> --known tools/s7467_san_reviewed.tsv. Needs an idle unlocked
screen (SOAK_NEEDS_IDLE header if queued). Also log a route-reached marker per leg (hangar entries count, initMission count).
