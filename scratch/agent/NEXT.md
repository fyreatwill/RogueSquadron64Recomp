Single next work unit (s5641): fold s5640_speech_{a,b} (grep '\[speech\]' scratch/agent/m6/<tag>/run.log).
Splits: no playObjectiveVoiceLine2 lines -> lv2 script never requests voice (trace the 9 lv2 sites' conditions / objective bools; oracle at mission start for expected order). Line2 present but playSpeechClip g8E/g8C/g72/w0B50 show a gate closed (g72!=0x10, w0B50!=0, g8E!=0) -> gate-state writer is the defect (name writer; compare to retail via oracle). Line2 + playSpeechClip pass all gates -> look downstream (stopVoiceByHandle / sound start / MusyX voice alloc / ucode PCM). playSpeechClip n=0 with control absent -> rebuild check.
Note: s5637/s5639 Line1 nulls are irrelevant to lv2 (it uses Line2).
HYPOTHESIS-ID: g2-voice-never-requested
