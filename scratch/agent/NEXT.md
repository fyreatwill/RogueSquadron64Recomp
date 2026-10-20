Single next work unit (s5646): is the voice slot's sample data non-silent, and does the ucode mix it?
Premise: s5645 fold showed slot 0x80153420 is serviced, completions arrive, consumeVoiceSamples runs (a1=0x8B/0x46), stream id 7 starts. Game log: scratch/agent/m6/<tag>/run.log.
Build ONE instrument (fixup script like tools/apply_s5644_voicedown_log.py): in consumeVoiceSamples log, for the first ~30 calls, nonzero-byte count + first 16 bytes of the buffer it reads (slot+0x11A4 region / source ptr), and in the audio ucode path (ROGUESQ_AUDIO_UCODE) count ADPCM/mix cmds whose source addr falls in that buffer. Positive control: same dump on a music buffer must be nonzero.
D1 buffer all zeros => PI DMA / ROM-bank read for speech yields zeros (find the DMA source addr, compare with ROM bytes).
D2 buffer nonzero, ucode never reads it => cmd-list builder skips voice (M5 de-stub target).
D3 ucode reads it and PCM nonzero => loss is later (AI ring / gain); compare with retail oracle.
Queue 2 soaks (m6_god_common.sh recipe as s5644_vdown) after the build.
HYPOTHESIS-ID: g2-voice-never-requested
