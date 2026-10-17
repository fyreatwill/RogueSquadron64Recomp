# Next: hangar-route flake as an evidence-based idiom-class audit
HYPOTHESIS-ID: hangar-flake-fault-class
Why this is allowed under directive 3: updateHangarBayScene+76424 (guest pc 0x800AC8C0, si_addr 0x4000cd6d3) is NOT a single crash. Ledger hits: s2290, s2511, s5010, s5085 (x2 runs), s5089 -- same pc, same signature, ~1 in 2 hangar routes. Recurrence is met; the goal is the CLASS, not a one-site guard.
Hypotheses (si_addr 0x4_000c_d6d3 is a 64-bit host address with bit 34 set, not a plain 32-bit guest address):
 H1 an unsigned/zero-extended KSEG0 base (guest 0x800CD6D3-ish) used without the sign-extension lowering (s2164 census class);
 H2 a stale/uninitialised pointer field read from a hangar-scene object (race with the image/audio worker, startup-order sensitive per s2511);
 H3 a recompiler lowering of an unaligned lwl/lwr or halfword pair at +76424 composing a bad address.
Discriminator (one offline step, no new run if an existing crash dump has it): disassemble guest 0x800AC8C0 (tools/agent/disasm_at.py), identify the base register and its producing instruction; compare to si_addr. Base loaded from memory => H2 (grep that load idiom class across generated funcs); arithmetic-op lowering => H1/H3 (census of that op class). Reuse crash logs in scratch/agent/s5085_stall_idle_try1 and s5090_logs.
Do NOT add a one-site guard; close the idiom class or prove it dead.
