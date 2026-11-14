# NEXT (s7337): idiom-class audit - hard-coded 8 MB "end of guest RAM" range checks
HYPOTHESIS-ID: stale-8mb-range-checks
Context: s7336 closed host arena layout (tools/s7336_host_arena_table.py). Its grep turned up a second idiom class: range checks
that hard-code 0x80800000u as the end of guest RAM. Since s6858 every dd>1 run tells the game it has 12 MB (guest top 0x80C00000),
so heap/fb/FIFO addresses in 0x80800000..0x80C00000 are legitimate there, and these checks quietly reject them.
Sites (grep -n '0x80800000u' src/main/main.cpp src/rsp/dpc_bridge.cpp lib/N64ModernRuntime/ultramodern/src/mesgqueue.cpp):
main.cpp 510 (rs64_ram_top initial value, fine), 537, 606, 1116, 1706, 4580, 4630, 4857, 5541, 5672; dpc_bridge 891 (pool range),
1682, 1733, 3551; mesgqueue 535 (s6572 queue cap exemption). Also check the generated-code fixups: grep tools/apply_*.py and
tools/fixup_*.py for 0x80800000 / 0x00800000 literals.
Hypotheses: H-diag (every site is diagnostic or logging only, so a stale bound loses log lines but doesn't change behaviour),
H-behave (at least one site gates behaviour, e.g. OSTask validation at main.cpp 4857 or a task_ptr/a0 check, and drops or mangles a
legitimate >8 MB address at dd>1), H-intended (the bound means "below the 8 MB retail heap" on purpose).
Method: classify every site statically: what it gates, whether a legitimate dd>1 address can reach it, and the right bound
(rs64_ram_top, the s7335 guest top, or keep it as is). Write the table to docs/HEAP-ADDR-AUDIT.md as class R. For any H-behave site,
switch it to RS64 guest top / rs64_ram_top behind ROGUESQ_S7337=0 and check it with one dd8 21:9 L1 arm plus a counter of how
often the old bound would have rejected an address (positive control: the counter is >0 in the dd8 arm and 0 at dd1).
