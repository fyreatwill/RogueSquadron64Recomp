# Next work unit (s4458): name the writer of the bad list link feeding musyxSynthFrame+5436

HYPOTHESIS-ID: m5-ai-event-cadence

State: s4457 added ROGUESQ_LOG_S4457=1 (last-writer table + list check, hooks at 0x8009133C head read / 0x80091378 next read). One +5436 hit showed next=0x80193C18 (off-grid) then 0xFCFFFCFF; fill pc 0x80061520 (byte 0xFF).
Hypotheses: (A) head/predecessor pointer overwritten by stray store (writer pc in [s4457-ptr]); (B) pool block freed+memset-0xFF while still linked (pc 0x80061520 caller); (C) stubbed/missing audio init leaves a node unlinked (head writer 0x8008F6CC/0x8008F7C0 sequence).
Discriminator: `[s4457-ptr]` line (lastw pc of the pointer leading to the bad node) on a +5436 hit. Reproduction rate is ~1/20 at hz115, so queue a soak recipe (scratch/agent/s4457_run.sh pattern, 6 arms x 120 s) and fold results; also consider making the fault deterministic via ctl arms (s4456 ctl hit 0x94fc 4/4 with the older binary).
Note: no `timeout` binary; concurrent arms only; scratch/agent/s4457_run.sh is the harness.

s4458 result: rerun of s4457_run.sh gave 0/6 +5436 hits (crashes: initVec4TripletFromArgs+308, advanceSongRegion+7536). Rate is too low to wait on; next unit should make corruption deterministic (hook the 0xFF memset caller 0x80061520 / pool-free path and log frees of still-linked nodes in one run) or enqueue a longer soak via scratch/agent/soak_queue and pivot to M5 plan steps.
