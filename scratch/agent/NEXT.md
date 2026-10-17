# Next: complete indirect-control-flow idiom-class audit (M3), offline

The M3 j/jal list is exhausted (s5349), but that is one idiom class. Audit the
remaining classes over the generated code and ROM, offline, no toolchain needed:
(a) every `jr $reg` / `jalr` site: classify as return, jump-table, or computed
    call, and check each jump-table's targets are all recompiled function entries
    or in-function labels;
(b) lwl/lwr/swl/swr pairs: confirm each pair is emitted as a matched unaligned
    access and none is split across a function boundary;
(c) branch-likely delay-slot nullification on the not-taken path.
Positive control: a known-good site from each class must be found by the same
script. Output a table class -> sites -> unresolved count in docs/.

HYPOTHESIS-ID: m3-indirect-idiom-class-audit
