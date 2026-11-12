# NEXT: guard-refusal livelock class audit (CURRENT-TRUTH item 1)
HYPOTHESIS-ID: guard-refusal-livelock-class
Context: s7194 fixed one member of this class. An external message to an mq that mesgqueue_guard refused was requeued forever, and
the v1 recipe froze 5/5 on the old path vs 5/5 OK with the fix. The same refusal returns appear at about 10 other sites in
lib/N64ModernRuntime/ultramodern/src/mesgqueue.cpp (osSendMesg, osJamMesg, osRecvMesg, do_recv, do_recv:msg, osCreateMesgQueue,
vi-deq), and possibly in the thread/timer/event code (grep `refuse\|rs64_ram_top` across ultramodern/src and src/main).
Unit (offline first, s282-s288 class-audit model):
 1. Enumerate every guard-refusal return in ultramodern/src + src/main shims. For each one, record what the caller sees (return
    value, mq state) and whether any caller loops on it. Look for guest retry loops: osRecvMesg BLOCK returning -1 at once inside a
    `while (osRecvMesg(..) == -1)` or a scheduler loop, timer re-arm on a refused mq, and event registration (osSetEventMesg) to a
    refused mq that would post every VI.
 2. Classify each one as SAFE (it returns and the caller moves on), DEAD (unreachable), or LIVELOCK (a retry-forever shape). Fix each LIVELOCK
    the way s7194 did (drop + log once, env to restore the old path), with a forced positive control that hits it on demand.
 3. If all are SAFE/DEAD: close the class in CURRENT-TRUTH with the table, then take the next ladder rung (item 3c).
Hypotheses: H-one (the s7194 site was the only livelock) vs H-more (another refusal path spins: e.g. a refused osRecvMesg BLOCK
returns at once, the guest loops, and the thread never yields).
Outcome: the table is the discriminator. Any LIVELOCK row needs a forced arm that freezes on the old path and heals with the fix,
same as s7194.
