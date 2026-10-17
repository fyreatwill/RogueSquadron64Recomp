# Next: does the ROGUESQ_FREE_CENSUS=1 stall reproduce on the current binary?
HYPOTHESIS-ID: nohangar-intermittent-flake
s5058: baseline recipe (census off) reached hangar 3/3 (+1 in s5057). Remaining known delta from the earlier 0/8 stalls: FREE_CENSUS=1 (s5044, single-source 4/4 stall vs 3/3 pass).
H-census: census hook perturbs the route (stall). H-flake: earlier stalls were transient state; census runs now pass.
Run: copy scratch/agent/s5048_preS5038_source.sh to s5059_census.sh with `ROGUESQ_FREE_CENSUS=1` added to COMMON and a distinct NAME; run it 3x (one at a time), copy keys1.log each time. 3/3 stall = census causes it (then find the writer: what the census perturbs). 3/3 pass = transient, resume the poison-on-free read-after-free probe (s5041 next step). Mixed = flake rate with census.
