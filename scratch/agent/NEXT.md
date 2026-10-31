# G1(d): level8 live train-car ownership + one disable (kind-12) response
HYPOTHESIS-ID: g1-coverage-cd

s6687 static contract (docs/G1-OBJECTIVE-RESPONSE.md s6687, `--check-level8`):
win = counter5==7 (one latched "disable" per train car, kind-12 damage message
draining DAT+C4+4*detail in npcTrainCarUpdate 800E2818, tuple +AC at 800E3B38);
loss = counter3==1 (hull death of any non-engine car, tuple +70 at 800E3D70)
or Boolean5 (EVENT_train_pulls_in). Cars are spawn category 2, ungated.

Hypotheses for the live run:
H-owned: train cars register (desc+6 != FFFF) during the scripted route ->
  one ordinary kind-12 message to a registered car can be admitted.
H-late: cars register only after some event/phase (not in the first 90 s)
  -> record the VI where they appear; no response attempt.
H-kind: our request API cannot emit msg+4==12 (it sends some other kind)
  -> would hit the HULL route = mission failure: do NOT send; record the
  kind the API emits and stop at that boundary.
Discriminator: one run logging per-car desc+6 slot over time AND the message
kind the existing request path writes at msg+4 (read from the code, before
any run: tools/apply_s6657_objective_response.py request builder).

Steps:
1. Read the API10 request builder; establish what msg+4 kind it writes.
   If it is not 12 and cannot be set to 12 through the original API, run an
   ownership-only arm (no requests).
2. Extend tools/g1_objective_response_run.py choices to level 8 (and the
   adapter, ordinary-only, lethal/TELE disabled), regen in order, build.
3. env ROGUESQ_LOG_GRIDSPAWN=1 python3 tools/g1_objective_response_run.py s6688_lv8 --level 8
   Screen must be unlocked. Same-run controls: some changing value
   (e.g. a gridspawn activation or Boolean8/6 proximity set) must fire.
Constraints: no FFFF fallback, no hull/lethal request, no direct stores,
no threshold forcing, no win attempt (counter5 7/7 is owner playtest).
