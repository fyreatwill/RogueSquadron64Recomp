# Next work unit: M5 Step 9u — what does 0x800AF60C (save/EEPROM load) put in the stack buffer at sp+0x18..0x8A, port vs retail?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4222 chain: zero gain words <- zero channel volume <- cmds 0x15/0x16 a0=0 <- applyVolumeSettingsToMixer reads 0x80130B60..62 <- zeroed at 0x800A6528/6530/653C from stack bytes sp+0x88..0x8A of the function containing 0x800A64BC..0x800A6568, filled by `jal 0x800AF60C` (a0 = *0x800B0AFC, a1 = sp+0x18) at 0x800A64CC. Retail runs the same PCs at ~17.0 s and ends with 0x7F.

Hypotheses:
- H-save-load-returns-blank: port's EEPROM/pak read returns zeros (no save file / stubbed osEepromLongRead), retail's returns 0x7F or the loader falls back to defaults on a valid-checksum blank.
- H-loader-validity-branch: the loader validates a checksum/magic; retail takes the "invalid -> defaults 0x7F" branch, port takes the "valid -> raw copy" branch (or vice versa).
- H-stack-buffer-clobber: buffer is correct on return but clobbered between 0x800A64D0 and 0x800A6528 (port-only), e.g. by a stubbed callee (0x800668B0, 0x800AEB30/F260/EB38).

Discriminator (one build, one run): port hook at 0x800A64D4 (right after the 0x800AF60C return) dumping sp+0x18..0x8C words + v0, and at 0x800A6528 the same bytes; retail twin `--watch-pc 0x800A64D4` and `0x800A6528` (oracle prints a0.. only; add --pc-field-dump or a mem read if needed, else watch writes to the stack via --watch-write on the physical sp page). Positive control: retail 0x800A6528 must show 0x7F bytes. Split: buffer zero at 64D4 -> H-save-load/H-loader (then inspect 0x800AF60C's EEPROM read vs port osEepromLongRead/save path); nonzero at 64D4 but zero at 6528 -> H-stack-buffer-clobber.

Reuse: tools/apply_s4222_vol.py (ungated hit log pattern), scratch/agent/run_s4222_retail_v.sh (watch template). Port boots crash ~1/3 starts (known); rerun.
