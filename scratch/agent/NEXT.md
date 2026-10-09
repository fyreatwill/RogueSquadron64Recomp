# Next work unit (s4429): port-side comparison of the title heap bytes

HYPOTHESIS-ID: m5-selector-copy-lifetime

s4428 (retail): the 16-byte name copy at 0x80007670 lands on zeroed pre-heap
memory at 0x80171CD0/0x80173B10 (over the future malloc headers) and on the
user words 0x80171CE0/0x80173B20 at origin 0x00696600; the heap is carved
afterward (headers 2/0x1E30, 1/0x21480 at the publish sw, origin 0x00790500).

Hypotheses for the port:
- H-port-same: port shows the same copy and same bytes at the title load.
- H-port-no-copy: port never runs the copy to these addresses (different
  heap layout/pointers) so user words are zero/garbage at the load.
- H-port-heap-first: port carves the heap before the copy, so the copy hits a
  live block or is overwritten.
Discriminator: one port run, same two moments (copy sb, publish sw), print
header half/size and user words at both. Outcomes split the three directly.
Control: whole-image store counter must fire; require the title load row.
Use the port's existing store-field/watch tooling (grep CURRENT-TRUTH s4416
and tools/ for the port-side witnesses); no heap rewrite or guard.
