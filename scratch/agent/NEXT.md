# NEXT (s7527)
HYPOTHESIS-ID: host-libultra-side-effects

Check `wc -c < docs/CURRENT-TRUTH.md` first (it is 59.2 KB after s7526; >60000 = MAINTENANCE iteration instead).

rsp-task-v2p is CLOSED (s7526 same-run twin H-same + ctl; owner decision row in docs/OWNER-OPT-INS.md). Its lesson names a class:
**class FU — retail side effects skipped by host replacements of libultra.** s7524 found osSpTaskLoad_recomp skipped retail
_VirtualToPhysicalTask. Enumerate EVERY guest function the port replaces or ignores (N64Recomp toml ignored/renamed/stubbed lists,
librecomp/ultramodern *_recomp entry points, fixup_game_funcs.py overrides) and, for each, list the retail routine's side effects from the
ROM disassembly (RDRAM writes, register writes, cache ops, address conversions, global state it updates) vs what the host version does.
Classify each row: H-canon (all effects reproduced), H-dead (effect unobservable by any reader: name the readers), H-gap (effect skipped and
read by someone -> measure it, s7524 style). One tool (tools/s7527_host_replace_audit.py) producing the table, with a positive control:
the osSpTaskLoad row must come out H-gap without V2P and H-canon with the s7524 path counted.
Expected: most rows H-canon/H-dead; any H-gap row gets a same-run measurement next session.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
