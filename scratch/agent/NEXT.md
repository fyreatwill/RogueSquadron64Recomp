# NEXT (s5886): who enqueues the msg-5 that kills class-2 objects?
Context (s5885): all 14 destroy arrivals at updateDestructionDebrisNpc come with msg=5; entry ra is 0 (host dispatch). s5884: SEND hook saw 0 descriptor victims. So the post path or the victim decode differs.
Hypotheses: (a) msg-5 posted by a different routine than the SEND we hooked (area damage / collision-resolve); (b) SEND victim decode wrong (slot index vs descriptor).
Discriminator: hook the dispatcher's queue-post function (find via funcs_8 slotDispatcherIter's inbox write) logging msg==5 with caller ra + target slot, join against the destroy-ctx lines by slot->desc (+0x34). Positive control: class-0 destroys must join too.
Run: zsh scratch/agent/s5885_ctx.sh (rename tag).
HYPOTHESIS-ID: g1-mission-progression
