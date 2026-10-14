# Next work unit (M5 task-family retail comparison)

HYPOTHESIS-ID: m5-task-family-retail-compare

s4860 showed the port publishes one stable audio task family (task 0x80149470,
type 2, ucode 0x80099FE0/0x1000, ucode_data 0x800A4E00/0x800, data_ptr
0x80171CE0 title / 0x80171E70 hangar, data_size mostly 1). Port-only evidence.

WORK UNIT: use tools/oracle (retail ROM, mupen64plus) to read the same OSTask
at physical 0x00149470 (+words) and the data_ptr/data_size at title and hangar
VI phases, after the whole-RDRAM positive control (~10000 hits). Compare with
the port table.

Hypotheses: H-retail-match (same ptr/fields/data_size=1 -> task contract
cleared, drop it from M5 backlog); H-retail-differs (data_size or ucode_data
differ -> name the writer before any fix, rule 11); H-oracle-invalid (control
or VI phases missing -> unevaluable).
Discriminator: retail field words vs the s4860 table in
scratch/agent/soak_results/s4860_m5_task_family/verdict.txt.
