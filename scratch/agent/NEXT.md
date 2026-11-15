# NEXT (s7380)
HYPOTHESIS-ID: host-condvar-lost-wakeup

s7379 closed AU2 (resize teardown vs present: H-ordered, probe ROGUESQ_S7379_PROBE=1 0/56 + 0/75 under resize stress, TSan rc 0).
Item 1 of CURRENT-TRUTH Next steps is now class AV: a new idiom-class audit (ITERATION.md 3 model: enumerate, classify every
site, fix or prove safe, close).

Work unit: class AV, every host std::condition_variable / condition_variable_any (22 declarations across src/, lib/rt64/src,
lib/N64ModernRuntime, excluding contrib) and every .wait / .wait_for / .wait_until / .notify_one / .notify_all on them.
Per wait site record: mutex held, predicate form (lambda / while-loop / NONE), what other mutexes are held across the wait,
the state the predicate reads. Per notify site: is the predicate state written under the SAME mutex the waiter holds (a write
outside it, or under a different mutex, is a lost-wakeup window), notify before vs after the write, notify_one where several
waiters can exist, shutdown flags (threadsRunning / presentThreadRunning) written without the mutex.
Hypotheses: H-clean (every pair writes predicate state under the waiter's mutex), H-lost (>=1 pair writes outside it: hang
until the next unrelated notify; candidate mechanism for rare stalls), H-shutdown (only the stop flags are unlocked: exit-time
hang, harmless in play).
Known leads to check first: RT64 PresentQueue::~PresentQueue sets presentThreadRunning=false with no cursorMutex before
cursorCondition.notify_all; WorkloadQueue threadsRunning likewise; the s7378 interpolatedCondition pairs; ultramodern
events.cpp / mesg queues; plume_metal present wait.
Discriminator: a census tool tools/s7380_condvar_census.py (--check exits 1 on an unreviewed or LOST row, --controls plants a
pair with an unlocked write and must flag it) + hand-verdict TSV. Any LOST row: fix (write under the mutex), gate with a
targeted stress (e.g. a delay injected between the unlocked write and the notify must hang the old arm and not the new one =
positive control), smoke `env SECS=260 zsh scratch/s7326/run.zsh s7380_dd8 ''`, TSan via scratch/s7379/tsan_run.zsh copy +
`python3 tools/s7354_tsan_report.py` rc 0.
