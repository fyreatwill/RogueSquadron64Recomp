# NEXT: which compare rejects the span cell
HYPOTHESIS-ID: g1c-span-reject-predicate

s6514 closed the writer question. EMPTY returns read populated primary span
bytes, then `0x80042DB4`/`0x80042DC0` stamp `0x7F`. The second plane was 127
on 100/100 dd4 EMPTY first samples and 25 on 6/6 dd1 EMPTY samples. That is
not yet the compare predicate: cell+3 and cell+4 were not logged.

One Debug build, one pinned dd1/dd4 run. At `0x80042D8C` and `0x80042DA4`,
count clears caused by span < cell+3 versus cell+4 < second-plane, and log
the two cell bytes with the span bytes on the existing keyed return. Keep
`[span-base]`. Do not add a guard or change behavior.

- H-s1-sentinel: dd4 EMPTY clears are cell+4 < 127 on the second plane; dd1
  EMPTY and nonempty accepts are not.
- H-s0-below: clears are span < cell+3 in both arms.
- H-both: both predicates fire on the dd4 EMPTY rows.

A null is invalid unless `[span-base]` fires in both arms and nonempty rows
still show `npass>0`.

Commands:

    python3 tools/apply_s6515_span_predicate.py
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/s6515_span_predicate.sh
