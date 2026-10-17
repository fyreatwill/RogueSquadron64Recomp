# Next: fold s5099 soak verdict, then M3 class: bare int/unsigned locals as MEM_x base
HYPOTHESIS-ID: m3-idiom-class-audits

1. tail -5 scratch/agent/SOAK-RESULTS.md: s5099_shape3_fix_soak should show rc=0 and keys.log hangar_arrivals>=2 crash=0. If it crashed, grep the run logs for the crash symbol before anything else.
2. Audit bare `int`/`unsigned` locals used as MEM_x base in fixup-emitted code (extend tools/audit_uint32_s32_base.py's pattern with a selftest control).
3. Then remaining host wrappers: osViSwapBuffer, EEPROM/pak buffer args (guard-class audit).
