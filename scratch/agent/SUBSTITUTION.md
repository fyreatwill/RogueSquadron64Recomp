1. The planned physical PIF-range read-watch arm could not produce a valid
   observation: the oracle exited `rc=139` before its first VI. Removing the
   whole-RDRAM watch reproduced the same failure, so this was substituted with
   a read-watch-path isolation check.

2. This iteration's evidence: the PIF-read watch crashed twice at the same
   pre-VI RDRAM-initialization point, while a same-configuration whole-RDRAM
   write-watch control completed with 1,082,129 hits and 287 VI frames in 5
   seconds. The positive control visibly fired.

3. Refutation experiment: run a read watch on an ordinary mapped RDRAM word in
   the same oracle binary/configuration. If it also crashes before VI, the
   generic debugger read-watch path is the blocker; if it survives, the PIF
   region mapping or handler is the blocker.
