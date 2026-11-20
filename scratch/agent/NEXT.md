# NEXT (s7705)
HYPOTHESIS-ID: wide-fb-readback-flight-s7705

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.

s7704 closed the boot-cinematic case: at 21:9 the game's previous-frame copy (768 wide, write-back skipped by SKIP_WILD_W) never reaches the
screen (write-back on/off pixel-identical, magenta ROGUESQ_S7704_POISON=768 fill invisible, RT64 serves 0 loads from its GPU fb at 21:9).
Open remainder (CURRENT-TRUTH item 25): does any OTHER reader of a skipped wild-width buffer exist in 21:9 mission flight or an intro cutscene?
Hypotheses: H-none (the boot cinematic is the only fb read-back, so the skip is harmless everywhere) / H-flight (flight or cutscene reads a skipped
buffer, e.g. a 1024-wide FB_WIDTH image is allowed but some other width is skipped) / H-dma (the RSP reads a skipped buffer by DMA, not texture).
Discriminator, ONE run at the owner 21:9 recipe (FPS60 dd2 ASPECT=21:9) on a forced level with an intro cutscene (L1, scratch/s6899/arm.zsh template
or tools/s7696_cut_standins.zsh), with ROGUESQ_S7702_FBREAD=1 (texture + DMA hits, keyed by image/width/age) and LOG of SKIP_WILD_W. Join fresh-image
(<5 s) hits against the SKIP_WILD_W address list. Positive control: the s7702 live control (ctl_live n/n) plus the boot-cinematic hits in the same run.
If a fresh hit lands in a skipped buffer: run tools/s7704_wide_fbcopy_arms.zsh-style poison arms on that scene (POISON=<width>) and look for
magenta in presented frames. If none: close item 25 entirely.
