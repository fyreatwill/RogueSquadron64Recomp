# NEXT (s7863)
HYPOTHESIS-ID: g3-audio-clock-sign
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. A crash or owner report outranks this.
State: det sweep 0..18 complete (s7862, `python3 tools/s7862_det_sweep_table.py`): 17 H-exact, 3 FORK = audio-clock (0x31=8, 14,
bonus 17). In all 3 the PORT's song ends 1 tick early. b17 (scratch/s7861/v17, `python3 tools/g3_song_windows.py r1/oracle.log
p1_rand.txt`): song 01 640/640 AI buffers (equal), song 02 retail 1872 / port 1869, song 03 retail 643 / port 640. 0x31=8: 643/637.
s6806 called the natural-end cues parity within 1% but never asked about the sign.
Hypotheses:
- H-buflen: retail's extra buffers are SHORTER (musyx/AI frame length varies with emulated audio-thread timing); samples per
  song window are equal, so the song ends on the same sample count and the split is retail CPU timing (timing class, close).
- H-rate: port synthesises more samples per buffer or per VI (a real port audio-rate defect, 3/640 = 0.5% fast).
- H-retail-jitter: retail (mupen CPO=1) delivers AI interrupts late now and then, so the guest queues extra buffers; check by
  retail CPO=1 vs CPO=3 on the same window (s7828 did this for frame rate).
Discriminator, ONE offline step then ONE run: (1) disassemble runAiAudioStreamPlaybackLoop around 0x8008EE08/0x8008EE84
(`mips64-elf-objdump` on the ELF from make_elf.py) and find where osAiSetNextBuffer's length (a1) comes from (register or a
memory word). (2) Add that length to both sides' AI rows (RS64_XTRACE_MEM / ROGUESQ_XTRACE_MEM with the struct+off, or a new
oracle/port xtrace field for a1 if it is register-only) and rerun bonus 17 only (shortest, 1738 ticks; s7861 recipe in
CURRENT-TRUTH item 12, REC can stay on). Score: sum of buffer lengths per song window per arm.
  equal sums, retail more+shorter buffers -> H-buflen (close as timing class); port sum larger -> H-rate (find the synth step);
  retail sums vary with CPO -> H-retail-jitter.
Positive control: song 01 (640/640) must give equal sums AND equal counts; the tool must flag a planted +1 length.
