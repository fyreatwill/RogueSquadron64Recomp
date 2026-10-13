# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

s4734: runaway frames (port 1846/1849/1851) are a DL walk that, after the 3rd scene block, jumps back to the start-of-frame setup (`3f 37 36 27`) instead of continuing to the HUD block; blocks repeat byte-identical up to 74x, ~70-86 ring wraps per task.

Work unit: in the port's F5 ucode DL walker (src/rsp / factor5_ucode), log every G_DL / G_BRANCH_DL / G_ENDDL (call/return/branch) with (task#, from_addr, target, stack depth) for tasks that wrap the ring >5 times; find the target that equals an earlier already-visited address.
Hypotheses: H-stale-return (DL stack pop yields old address: stack overflow/underflow or missing push), H-cyclic-data (game-side DL linked list genuinely cyclic: check same in retail via oracle watch), H-seg (segment-table entry wrong at that branch → resolves to frame start).
Discriminator: runaway task's jump target vs. address of the first block; if return stack depth is 0 at an ENDDL/pop => underflow (H-stale-return); if target comes from RDRAM DL data pointing back => H-cyclic-data (then compare that RDRAM word with retail).
Positive control: same logging on normal frame 1845's task must show monotonically forward targets.
Scripts: scratch/agent/s4734_*.py (offline), /tmp/s4733.pkl regen via s4733_cmp.py.
