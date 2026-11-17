# NEXT (s7551)
HYPOTHESIS-ID: class-gk-writeback-stale-native-columns

GJ CLOSED s7550: RT64 writebacks use current-command addresses and extents. Residual: copyNativeToRAM writes FULL rows
[drawRect.top, min(bottom, fb.height)) x colorImg.width, but the pair only drew drawColorRect's columns. The other columns' bytes
come from the native target, refreshed from RAM only when checkRAM's XXH3 differs at checkRDRAM (DL start, interpreter thread).
A guest CPU write into the span between checkRDRAM and the writeback (e.g. a CPU-drawn HUD/text pass, a heap block reused inside
a fb carve) would be silently replaced by older native content.

Hypotheses: H-clean (0 such bytes: the guest never CPU-writes an fb span during a DL in flight); H-clobber-benign (bytes overwritten
but the guest rewrites them before the next read / they're the same values); H-clobber (guest-written bytes lost, guest or VI reads
them -> visible defect or data loss).
Discriminating measurement, ONE build, ONE env (ROGUESQ_S7551_GK=1, default off, in lib/rt64 -> export.sh + commit):
  at checkRDRAM, snapshot (copy) RAM of every fb span that a pair in this workload will write back (or simply every registry fb
  with RAMBytes <= 1.2 MB, phase-budgeted); immediately before each copyNativeToRAM, diff RAM vs snapshot over the write span
  -> guest_changed_bytes; after the writeback, count how many of those bytes now differ from the guest's value -> clobbered_bytes,
  split inside/outside drawColorRect columns; log per phase writer address range (first changed offset) and the guest PC if the
  s7539 store-watch hook can name it.
  Positive control (same run): ROGUESQ_S7551_GK_PLANT=1 makes the host write a marker pattern into an undrawn column of the
  span right after checkRDRAM; it must show up as guest_changed and clobbered.
Arms, all built in one iteration and run one game at a time: L1 dd1 (retail), L4 dd4 16:9,
L12 dd4, owner recipe FPS60; >=120 s flight each, plus title/hangar.
Outcomes: clobbered 0 outside the plant -> H-clean, close GK. Nonzero -> name the guest writer (store watch) and decide whether
the fix is a column-exact writeback (only drawColorRect columns) or re-hash at fullSync before writeback.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
