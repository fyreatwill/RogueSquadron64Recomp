# NEXT: G1 - s5858: where are ~97% of hit SENDs dropped before dealDamageToNpc?
s5857: SEND=505 vs dealDamageToNpc=14 in one run; those 14 show hp pre==post and garbage hp (hp read has no positive control - void).
Hypotheses: H16 slotDispatcherIter does not deliver msg 5 to the victim (slot/ctx lookup fails, message queued/dropped); H17 delivered, handler (fn 0x800E7860, funcs_39.c:25943) takes another branch (type-5 index 4 -> L_800E84B8 skipped / health<=0 'blez' at 0x800E84C4 with hp already <=0 -> only sender cleanup); H18 delivered to NPCs whose fn is not class-1 handler (different update fns ignore type 5).
Discriminating measurement (one build): per run histogram of (a) slotDispatcherIter calls from the 0x8005D35C site, (b) handler entry count by msg type (a1) in npcGroundTroopUpdate, (c) entries at L_800E84B8, (d) hp read at 0x800E84C4 (blez) via the handler's own register, as the positive-control-able hp. Outcomes: (b)=~0 -> H16; (b)~SEND but (c) low -> H17; (b) low but SEND high -> H16/H18.
Run: env ROGUESQ_LOG_HITS=1 zsh scratch/agent/g1_fireall.sh s5858 300   (add hooks to tools/apply_s5857_dmg_log.py or a new apply_s5858)
HYPOTHESIS-ID: g1-mission-progression
