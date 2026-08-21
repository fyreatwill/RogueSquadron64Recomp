# NEXT work unit (s2085)

HYPOTHESIS-ID: m5-source-host-span-join

## Work unit

Perform one bounded source/host span join on the qualified s2084 capture.
Use the existing `[m5-fill-range-source]` rows and `[m5-host-boundary]` rows
from the same run; do not add another diagnostic field or change the binary.
Join by target phase, source `a1_dram..a1_dram+a2_count`, host `range`, guest
identity, and log order. The source row is an observation of the generated
writer's incoming arguments, not permission to treat those values as
legitimate or to add a mitigation.

## Competing hypotheses and discriminator

- **H-SourceSpanReachesHost** — at least one target-phase source interval
  intersects or equals a later/same-phase host `copyToRAM` range, with a
  compatible guest identity or a documented ordering relationship.
- **H-HostNoSourceMatch** — target-phase host rows exist, but none has a
  matching source interval; the host operation is therefore not joined to the
  observed fill entry at this scope.
- **H-SourceArgsAlreadyOutOfRange** — the source entry receives an interval
  outside the 8 MiB RDRAM domain or with an invalid count before any host join;
  this identifies an upstream/generated-input boundary, but not the writer
  that produced the value.

The discriminator is one post-hoc table from `scratch/agent/s2084_port/run.log`
that prints every target-phase source interval, every target-phase host range,
the intersection count, source/host line order, and guest PCs. A valid
in-RDRAM source interval that intersects a host range selects
H-SourceSpanReachesHost. Zero intersections with valid source intervals
selects H-HostNoSourceMatch. Any source interval outside `[0,0x800000)` or
overflowing that domain selects H-SourceArgsAlreadyOutOfRange. The join is
not interpreted unless the same run retains the retail whole-RDRAM positive
control, both target VI phases, the host control, and the source-entry rows.

## Ground truth and exact commands

Do not start a new game or build for this unit. First verify the independent
controls already captured by s2084:

```sh
grep -n -E '\[oracle\] (done|watch write|watch pc)' scratch/agent/s2083_oracle/run.log | tail -20
grep -n -E '\[vi\].*origin=0x006ab400 width=512|\[vi\].*origin=0x00790400 width=1024' scratch/agent/s2083_oracle/run.log | head -5
grep -n -E '\[phase\].*vi_width=(1024|512)|\[m5-host-boundary-control\]|\[m5-fill-range-edge\].*target=1|\[m5-fill-range-source\]' scratch/agent/s2084_port/run.log | tail -40
```

Run the complete same-run join without creating a second instrument:

```sh
perl -ne '
  if (/\[m5-host-boundary\].*phase=(\d+).*guest_pc=(0x[0-9A-Fa-f]+).*range=\[(0x[0-9A-Fa-f]+),(0x[0-9A-Fa-f]+)\)/) {
    push @host, { line => $., phase => $1, pc => $2, lo => hex($3), hi => hex($4) };
  }
  if (/\[m5-fill-range-source\].*source_n=(\d+).*phase=(\d+).*guest_pc=(0x[0-9A-Fa-f]+).*a1_dram=(0x[0-9A-Fa-f]+).*a2_count=(0x[0-9A-Fa-f]+)/) {
    my ($n,$phase,$pc,$a1,$count) = ($1,$2,$3,hex($4),hex($5));
    my $end = $a1 + $count;
    my @m = grep { $_->{phase} == $phase && $a1 < $_->{hi} && $end > $_->{lo} } @host;
    my $valid = ($a1 < 0x800000 && $end <= 0x800000) ? 1 : 0;
    print "source line=$. n=$n phase=$phase pc=$pc span=0x", sprintf("%X",$a1), "..0x", sprintf("%X",$end), "valid=$valid matches=", scalar(@m), " host_lines=", join(",", map { $_->{line} } @m), "\n";
  }
' scratch/agent/s2084_port/run.log
```

No wait, guard, task, canary, gate, output, or host behavior change is
authorized.
