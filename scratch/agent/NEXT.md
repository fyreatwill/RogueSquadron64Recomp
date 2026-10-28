# NEXT: px3 limit = allocAndInitDoublyLinkedNodePool12 returns NULL (s6568)
HYPOTHESIS-ID: g1c-dd-phase2
Fact: px2 clean with ROGUESQ_DLPOOLX=1 (+DLPOOLX_MB=4, _AT=3000, RAMTOP_MB=16); px3 5/5 crash at allocAndInitDoublyLinkedNodePool12+2588, si_addr=0x380000002 (NULL+2). Arena not exhausted.
Hypotheses: H-heap (guest rs_malloc/heap alloc inside that function returns 0: heap full at px3 -> needs 2nd arena / bigger heap); H-count (node count scales with dd and exceeds a fixed table); H-ptr (caller passes NULL pool header).
Discriminator: read the generated allocAndInitDoublyLinkedNodePool12 source near the +2588 fault, name the callee that returned 0 (log its args/ret under env), run px3 once with that log. Also repeat px2 D arm 2x for reproducibility. One game at a time.
Repro: zsh scratch/agent/s6553_run.sh 6 3 "ROGUESQ_RAMTOP_MB=16 ROGUESQ_DLPOOLX=1 ROGUESQ_DLPOOLX_MB=4 ROGUESQ_DLPOOLX_AT=3000" F
