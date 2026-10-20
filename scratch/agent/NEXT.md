Single next work unit (s5645): fold s5644_vdown_{a,b} from SOAK-RESULTS.md / scratch/agent/soak_results/s5644_vdown_*.log (grep '\[vdown\]\|\[aloc\]').
Premise correction: queue 0x80154650 is a pool lock; consumer chain is serviceVoicePoolFrame -> serviceStreamingVoice(slot) -> consumeVoiceSamples, slot queue at slot+0x11AC.
Control: [vdown] serviceVoicePoolFrame lines (music) + [aloc] entry must appear; slotrecv line shows ok/empty counts.
D1' serviceStreamingVoice never called with the speech slot (no slotchg / no entry with slot addr) => look at serviceVoicePoolFrame's slot-selection gate.
D2 called, slotrecv ok=0 always => completion message never posted to slot+0x11AC (find who osSendMesg's it: PI DMA completion / stubbed audio thread => M5 de-stub target).
D3 recv ok and consumeVoiceSamples entries and slot tuple advances => voice runs; compare cmd-list/ucode (old items 3,4: PI DMA counts, ADPCM cmds by bank) next.
If a soak lacks the control, rerun; do not conclude from a null.
HYPOTHESIS-ID: g2-voice-never-requested
