# Session 5129 M4 mid-task accumulator audit

The required rename-sweep REVISIT used the independent retail oracle's cxd4
LLE RSP. The existing per-task VACC dump was retained as a positive control,
and a new env-gated dump sampled VACC every 256 RSP instructions during each
graphics task. The cxd4 source changes are outside this repository; the
reproduction contract is recorded in `tools/oracle/patches/cxd4-rsp-mid-dump.md`.

Run: `scratch/agent/s5129_m4_mid_acc.sh`, 75 emulated seconds, Rice/rdplog,
the qualified nine-Start schedule. The run reached 320, 640, 1024, and 512
wide phases, including hangar origins `0x006ab400/0x006ab800`.

Results:

- 2,090 graphics completion records aligned 1:1 with 2,090 RDP rows.
- 3,048,760 mid-task graphics samples grouped into the same 2,090 tasks.
- 577 live 512-wide tasks, including 289 hangar-origin tasks.
- Zero mid-task VACC lanes equal to `0x8000` in hangar, all 512-wide tasks,
  or any sampled phase; the completion dump also had zero.
- Positive control passed: the completion dump was 27,171,928 bytes and the
  mid-task dump was 207,315,680 bytes, with every graphics task represented.

Discriminator: this selects `H-retail-no-0x8000-mid-task` and rules out the
retail RSP accumulator, at both sampled mid-task and task-end granularity, as
the carrier of the hangar `0x8000` value. This is single-source oracle
evidence; it does not explain the port and does not authorize a mitigation.
