Work unit: fold the s5508 arms (s5508_im_base / _f2 / _f7, queued in soak_queue; results in SOAK-RESULTS.md, logs in scratch/agent/m6/s5508_im_<arm>/run.log).
Commands: grep -h '\[initMission\]' and grep -h '\[mfst\]' on each run.log; diff the sorted unique [mfst] name sets base vs f2 vs f7. Also note crash/stall and whether `B40 forced` line fired (positive control).
Hypotheses: H1 B40 at initMission selects mission content -> [mfst] names differ across arms (then M6 second-mission soak: hold f2 >=10 min x3). H2 B40 only drives config; content comes from record/DAT -> names identical, controls firing (then trace what initMission passes to 0x8005360C/0x80053288 loaders at 0x800FA4E8/A538). H3 override too late/early (control line absent or B40 re-written) -> move hook.
Fallback if soaks have not run: run them by hand one at a time via `zsh scratch/agent/soak_queue/s5508_im_base.sh`.
HYPOTHESIS-ID: second-distinct-mission-coverage
