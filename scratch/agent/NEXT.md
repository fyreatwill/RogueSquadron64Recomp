# NEXT (s7401)
HYPOTHESIS-ID: replaced-libultra-input-contract

s7400 closed class BJ (output contract): osContGetReadData err_no + __osDisableInt r2 fixed (ROGUESQ_S7400_CONTFIX default on).
Fold first: soak s7400_cont_levels (L5/L10/L15, pass = alive, 0 crash, 30 [s7400-pad] PASS / 0 STALE per level).

Work unit, class BK (replaced-libultra INPUT/argument contract):
1. Extend tools/s7400_replaced_contract.py (reuse bodies()) with --args: per replacement with live callers, which args it
   reads (_arg<N,...>, ctx->r4..r7, stack 16(sp)+), how (sign-extension: (int32_t)ctx->rN vs raw u64; TO_PTR/MEM_* on a guest
   pointer), versus the libultra prototype arity and special values: NULL thread = current (osSetThreadPri, osGetThreadPri,
   osStopThread, osDestroyThread, osStartThread), OS_MESG_BLOCK/NOBLOCK flags (osRecvMesg/osSendMesg/osJamMesg), NULL msg slot,
   OS_PRIORITY_* bounds, osWritebackDCache/osInvalDCache len 0 or >= cache size = whole cache, osAiSetNextBuffer alignment
   (8 B) and size (multiple of 8), osPiStartDma direction/size, osViSetMode pointer, osSpTaskLoad task fields.
2. Resolve the guest arg value at each live jal (s7392 resolve / s7399 val) and flag a site where the guest passes a value
   the replacement mishandles (H-arg) or an arg the replacement ignores but libultra honours (H-ignored).
3. Hypotheses: H-none, H-arg, H-ignored. Discriminator if static does not settle: per-fn runtime log of (args, outcome) on
   route tools/s7392_mq_run.zsh owner + RETAIL=1 with a planted control (relative to ctx->r29 only, s7399 lesson).
Fix any deviation behind a default-on env, =0 restores old, two-arm qualified in ONE build (s7400 model: PASS vs STALE).
