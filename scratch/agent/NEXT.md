# NEXT (s5666): fold s5665_dgate_{a,b}: why does the CPU decode (decodeAndFillVoiceBlock) not fill slot+0x198?
Fact (s5665, static): decodeAndFillVoiceBlock (0x8009C904) is the only writer of the voice buffer; it is called from the serviceStreamingVoice fill loop (0x8009C0E4) behind gates (11DD==1||11A0!=0, 11DE>0, 11D8-11D4<19C-0xA0, 11D0==0||11A4!=0||11D0-11CC>=0x25).
Instrument built: [dgate] gate snapshot for slot 0x80153420, [dec] entry log (control: total count any slot). Logs in scratch/agent/m6/<tag>/run.log.
Outcomes: [dec] slotHits==0 with [dgate] present -> read which gate field fails (H5); slotHits>0 but dst never in 0x801B2C60 range / buffer pointer wrong -> H6/H7; slotHits>0 and dst in range -> decoder writes, so overwrite later (H7).
HYPOTHESIS-ID: g2-voice-never-requested
