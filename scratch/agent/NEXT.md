# Next work unit (s4284): count ring-lap bump drops per commit and join to ODD cimg events

HYPOTHESIS-ID: m5-audio-destub-sequence

s4283: ODD cimg = old CF-triangle tail beneath a newer command burst; header existed at bump; no dup range starts in the commit. Hypotheses: E1) ucode laps the ring inside the task and rsp_dpc_submit's high-water filter (s_submit_last_end) drops the lap's bumps, so the overwrite never reaches RT64 as a range; E2) overwrite comes from a different task (cross-task, outside this commit); E3) CPU/guest store into the ring.
Discriminator: in dpc_bridge.cpp rsp_dpc_submit count, per commit, submits where end < s_submit_last_end (lap) or lo < s_submit_last_end (drop); at each ODD event print that commit's lap count and the first lap's lo..hi. E1: ODD commits have laps>0 and the ODD addr lies in a dropped span; E2: laps==0 in ODD commits. Positive control: run ROGUESQ_DPC_WRAP_FLUSH=0/1 arms concurrently; with =1 the ODD rate must fall (s4273: 12.4%->8.6%) and laps>0 commits must exist in both arms. Template: scratch/agent/s4283_walk.sh (env block), reset build/saves per arm.
If E1 holds: qualify ROGUESQ_DPC_WRAP_FLUSH default ON (CURRENT-TRUTH item 1), phase-gated on VI 640.
