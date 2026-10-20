# G2 audio fidelity - evidence table (s5687)

Owner report 2026-10-19: heavy fuzzy/noise layer on all audio, no dialogue.
Question: where does the noise enter (ucode PCM / AI ring-rate-format / host sink)?

| Layer | Hypothesis | Verdict | Evidence |
|---|---|---|---|
| ucode PCM | voice lattice saturated -> rails | CAUSE, FIXED | s5668: audioCompandS16 mis-jump from lagging labels (N64Recomp recompilation.cpp:874); tools/fixup_label_realign.py; rails 0 in 44/46 lattice calls. s5669: 0/330 AI rows with rail samples |
| AI cadence | per-VI AI event gave 11.4k frames/s vs 22047 needed -> underrun crackle | CAUSE, FIXED | s5672: ROGUESQ_AI_EVENT_DRAIN default 2048; zero-queue 3/24064 |
| AI rate/format | dacrate/byte order wrong | REFUTED | s4438: retail dacrate 2207 = 22047.9 Hz = port; s4239/s4242: byte order FNV-matches ucode output |
| Spectrum vs retail | port noisier than retail | REFUTED (single metric) | s5671: hf_ratio retail title median 0.200, port 0.20-0.24 |
| Dialogue absent | speech never requested/never reaches output | REFUTED | s5669/s5670/s5674: enqueueSpeechClip x6, windows 1.9-15x control level, >98% energy < 3 kHz, rail-free |

Residual (needs a human): intelligibility and any remaining masking can only be judged by listening to
scratch/agent/m6/s5674_raw/wav/enq*.wav and a fresh build. No automated discriminator remains that is not
already a single-metric proxy. G2 is CLOSED pending owner listen; reopen on a listening report.
Next rung: dialogue-timing lead (CURRENT-TRUTH Next steps #2, bool 7 via sayWhoaHim_v0x1FC) under G1.
