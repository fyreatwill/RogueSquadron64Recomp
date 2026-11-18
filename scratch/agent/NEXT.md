# NEXT (s7562)
HYPOTHESIS-ID: regen-fidelity-drift

19b(d) CLOSED s7561 (s7366 scope fix, s7363 clamp ternary; regen_replay ok). Unit: 19b(e) s7375 NOLOCK thread census.
`python3 tools/s7375_nolock_threads.py --check -v` -> OPEN 8, all s7472-s7521 diagnostic containers never reviewed because
s7375 is not run by tools/regen_replay.sh: main.cpp g_s7500_ctla_cls, g_s7503_livefn; upstream_compat.cpp s_s7472_seen,
s_s7475_seen, s_s7480_internal, s_s7480_pcs, s_s7488_pcs; s7521_ucode_watch.cpp seen_off.
Hypotheses: H-confined (each is touched by one thread or only inside *_locked helpers whose callers hold a lock -> verdict rows)
vs H-race (a gfx/task-thread writer beside a guest reader with no lock, e.g. s7480_store has gfx|guest|lambda@4388 callers ->
fix with a mutex, env-gated diag code only) vs H-attrib (the thread attribution is wrong: '?' callers unresolved).
Discriminator: per row, read every accessing function and its real call sites; any pair of distinct threads with an unlocked
write = H-race (fix + rerun the owning recipe's env on L4 for a liveness check). Then add
`python3 tools/s7375_nolock_threads.py --check` to tools/regen_replay.sh beside the s7366 gate; controls: s7375 --selftest PASS,
plant a scratch NOLOCK container touched from a std::thread lambda and the guest (must be REVIEW/OPEN), fresh regen_replay ok.
Then s7420_parser_census OPEN 1 (fixup_patches_host.py STANDALONE weak-blind, since s7490).
Then 19b(c): fold s7558_b40_ab when SOAK-RESULTS has it (voided 3/5 so far), then ask the owner about the B40 default.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
