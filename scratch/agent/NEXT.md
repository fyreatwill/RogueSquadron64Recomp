# Next work unit (s4282): locate the SetColorImage command that produced 0x130393 w1033

HYPOTHESIS-ID: m5-audio-destub-sequence

s4281: snapshot==live (0 DIFF over 9 runs) so hypothesis A (RDRAM changes mid-walk) is refuted (no DIFF positive control, single-source). Ring shows the walker near 4E22D0..4E2308 at the event, while the bridge range is 4E27B0..4E2A58.
Hypotheses: B) the cimg command is a real F-op word at g_s4271_dl whose w1 is 0x130393 (game wrote it; origin is the DL builder); C) the walker reached the word via a misaligned advance so triangle data was decoded as SetColorImage.
Discriminator: at the event print 16 words around g_s4271_dl and the ring tail with adv values; check whether the previous command's advance lands exactly on g_s4271_dl. Add a DIFF positive control (flip one snapshot byte). Script: scratch/agent/s4281_walk.sh.
