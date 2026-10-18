# Next work unit: fold m6_sel_c verdict, then run the plume title-boot loop under lldb (>=20 boots) until the si_addr=0x58 SIGSEGV recurs; read its backtrace and fix the writer.
HYPOTHESIS-ID: m6-mission-transition-endurance
- sel_a/sel_b: origin set ~identical to s5449 baseline => SEL_KEYS gave no verified mission change (no positive control). Stop stick-press variations unless the autopilot can read mission id from RDRAM as a control.
- Discriminator: lldb title-boot loop. Crash => real backtrace names the writer. 20 clean boots => plume guard (s5446) holds; move to M3 idiom-class audit.
