# NEXT (s7382)
HYPOTHESIS-ID: host-thread-qos

s7381 closed class AW (host spin-waits): barrier spins never wait in play, now condvar waits (ROGUESQ_S7381_BARRIER_CV=0 old);
guest osYieldThread polls 0 calls; VI deadline spin 3% of a core by design.

Work unit: class AX, every host thread the process creates (std::thread / pthread_create / SDL_CreateThread / dispatch
queues / RT64 Thread / plume Metal completion threads; src/, lib/rt64/src incl. plume, ultramodern, librecomp).
Per thread: creator site, name, QoS class / priority set at creation (default, ROGUESQ_QOS_ALL=1, GUEST_QOS, PRESENT_QOS,
VI_RT real-time policy), whether it runs in play, CPU time in play, which cluster it ran on (P/E), and whether it ever
blocks waiting on a lower-QoS thread (priority inversion: e.g. a USER_INTERACTIVE present thread waiting on a default-QoS
render thread).
Hypotheses: H-covered (every hot thread already gets an interactive QoS by default; QOS_ALL only matters under load),
H-gap (a hot thread at default/utility QoS in normal play: can land on E-cores, a G1b/G5c pacing lever),
H-invert (a high-QoS waiter blocks on a lower-QoS producer: the waits measured in s7380/s7381 name the pairs).
Discriminator: census tool tools/s7382_thread_qos_census.py (--check exits 1 on an unreviewed creator; --controls plants
a thread creation that must be listed) + one runtime dump (env ROGUESQ_S7382_QOS=1, default off): at 60 s and 200 s, for
every thread of the process: name, qos_class (pthread_get_qos_class_np on self at a hook, or thread_policy_get /
proc_pidinfo THREAD info from a sampler), user+system CPU us (thread_info THREAD_BASIC_INFO), so CPU share per thread in play
is measured. Positive control: a planted thread created at QOS_CLASS_BACKGROUND under ROGUESQ_S7382_QOS_CTL=1 must show
background QoS and its own busy CPU in the dump.
Run: `env SECS=260 zsh scratch/s7326/run.zsh s7382_qos 'ROGUESQ_S7382_QOS=1'` and the same with ROGUESQ_QOS_ALL=1 (two arms,
same build, sequential). Any H-gap row with CPU share > 5%: set its QoS at creation (env gate =0 old), smoke both arms.
