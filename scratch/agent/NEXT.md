# Next work unit (s4360): classify live retail range arguments

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4359 qualified oracle capture passed whole-RDRAM, reached hangar, and
captured 512 C904/C950 witness rows. The range was live in title at PCs
`0x80033D20..0x800340FC`, but the exact `0x80033FCC` watch still produced zero
typed task rows and zero joins. The range output cap prevented a hangar range
classification.

Competing hypotheses:

- H-consumer-nearby: a nearby range PC receives a valid type-2 OSTask pointer;
  its task fields can be joined to C904/C950.
- H-consumer-other-overlay: nearby PCs execute, but their `$a0` structures are
  not type-2 tasks in both qualified phase buckets.
- H-pre-filter-origin: a joined task row has source fields that already
  disagree with the C904/C950 input/selected fields.

Discriminating measurement: add one bounded range-argument dump that records
exact PC, phase, `$a0`, `MEM_W($a0)`, and the OSTask fields at `$a0+0x28..0x3C`
for every range execution, with phase buckets `0x00790800:1024`,
`0x00790400:1024`, and `0x006AB400:512`. Nearby valid type-2 rows select
H-consumer-nearby; only non-task rows select H-consumer-other-overlay; source
disagreement in a joined row selects H-pre-filter-origin. Keep the whole-RDRAM
control, C904/C950 witness, exact `0x80033FCC` task watch, and VI trace in the
same capture.

Expected commands: extend `tools/oracle/rs64_oracle.c` with the bounded range
argument dump, run `./tools/oracle/build.sh`, then repeat the known-good oracle
recipe from s4359 with SIGKILL watchdogs. First run the whole-RDRAM and
C904/C950 controls in that same capture; discard it if either control or the
target VI phases is absent.
