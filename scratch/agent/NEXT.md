# Next work unit

HYPOTHESIS-ID: m3-idiom-class-audit

s4716 closed the unaligned-access idiom classes (swl/swr/sdl/sdr/ldl/ldr; tools/census_unaligned64_stores.py). Closed M3 classes now: MEM_B/BU/H/HU/W/WU, LD, lwl/lwr, unaligned stores/64-bit.
Remaining candidates: LL/SC (likely 0 sites), LWC1/SWC1 base-register class (FPR data, base is a GPR pointer - check overlap with MEM_W census), jalr/jr indirect-call target class (function-pointer reads). Pick jalr/jr: enumerate every `jalr`/indirect dispatch site, classify the target register's source (table load / vtable / constant), guard or prove dead.
Discriminator: unguarded indirect target from a writable table => land guard in fixup script; 0 => close class with proof. If no candidate classes remain, go BLOCKED asking the owner for a mission-entry discriminator.
