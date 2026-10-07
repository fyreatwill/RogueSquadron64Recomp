# M5 Session 4152 — producer caller-state split

The rebuilt port and independent retail oracle were captured with the
whole-RDRAM positive control and both target phase gates. The first paired
attempt was route-invalid: the port crashed before title in
`spTaskSchedulerThread+9632`. A fixed retry added only a two-second launch
stagger, then reached title and hangar without a crash or abort; no guest,
audio, wait, cap, predicate, slot, or writeback behavior changed.

The retail `0x800078E0` field dump produced title rows with predecessor
`0x800052C4`, including `s0=0x801B1560`, `s1=0x18`, and nonzero source words.
The corresponding port title setup at `0x8008F2CC` used `s0=0xF`,
`s1=0x561F`, destination `0x80178C80`, length `0x298`, and zero fill. In
hangar, retail also recorded the `0x800AB694` predecessor with `s0=0` and
`s1=0x800D0000`; the port had the same state tuple at that callsite but still
used a separate source-construction context.

H-caller-state-split is selected: the caller state differs independently of
the known callsite difference, and the difference is phase/context-specific.
The port generated `ra=0` remains unusable as caller evidence. ORIGIN: the
legitimate retail `rs_memset` entry/body and port setup/store rows; no value
was suppressed or rewritten.

Evidence: `scratch/agent/s4152_m5_caller_state_join/`, especially
`verdict.txt`, the bounded summaries, and the raw paired logs.
