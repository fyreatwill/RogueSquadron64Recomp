# NEXT: s7206 interlaced-still fix follow-up — distinct images/s and 4:3 G3 re-score
HYPOTHESIS-ID: interlaced-still-present
Context: s7206 fixed RT64's fb address for interlaced double-stride VIs (ROGUESQ_VI_ILACE_ADDR) and refused stale VI-history
early presents (ROGUESQ_PE_STALEFIX), both default on. The title/backdrop stills now present 60/s through the current VI (were
20/s, or 60/s through a stale VI). Picture identical on the static title. Open: does the 60/s carry new images, and does the
new address change G3 fidelity on 4:3 interlaced menus?
Hypotheses: H-motion (the wipe/fade stills change per workload, so f1 shows ~60 distinct images/s where f0 showed 20),
H-static (redraws are identical; gain nil, fix is still correct), H-regress (the new address changes which fb RT64 presents on a
4:3 interlaced screen, e.g. Elite Rogues 512x448, and moves its angrylion score).
Discriminator, one build (current), arms ROGUESQ_VI_ILACE_ADDR=0+ROGUESQ_PE_STALEFIX=0 vs default:
 1. g5b_capture (<= 30 s, delete raw after scoring) of the boot window t 8-30 at the owner recipe; tools/g5c_frozen_runs.py /
    tools/g5d_distinct.py distinct frames per second in the title/wipe span. Positive control: flight-span distinct ~60/s.
 2. 4:3 retail settings: re-score the Elite Rogues / interlaced menus with the G3 kit (CURRENT-TRUTH kit list; 448-row needs
    FID_MAINRUN=1) in both arms; any change > the retail floor = H-regress -> fix or flip default.
Outcomes: distinct f1 >> f0 -> H-motion (owner-visible gain); equal -> H-static; score move -> H-regress.
