# NEXT: identify the width-bearing RSP input
HYPOTHESIS-ID: g1d-widescreen

Session 6191 selected the same phase-4 task identity in both arms: type 1,
data_size 0, ucode 0x80024A10, ucode_data 0x80038D00, and ucode_data_size
0x800. The two dominant root-DL addresses differ only by the wide-arm
relocation delta -0x3E200, while the same guest command source 0x8000834C
produces the extra wide central TEXRECTs. The exact width-bearing input is
still open.

Next work unit: add one phase-scoped trace at `rs64_run_lle_gfx` / immediately
after `factor5_gfx_runner` loads the task input that records, for each unique
phase-4 root DL, the first 0x100 bytes (normalized by the arm's root relocation)
and a hash/nonzero count of the `ucode_data` bytes copied into DMEM. Keep the
existing `[g1d-task]`, command-source, join, and copy probes enabled. Build
once, then run:

    zsh scratch/agent/s6179_g1d_rdp_words.sh

Compare the same two-root sequence and the corresponding root/ucode-data
records in the control and wide `fail_att1.log` files; require the existing
160 joins and 400 copy rows per arm as positive controls.

Competing hypotheses and discriminator:

- H-root-DL: normalized root-DL bytes differ at the width/scissor input while
  ucode-data hashes match; the game-side DL input is the producer.
- H-ucode-data: root-DL bytes match after relocation but the bootstrap/DMEM
  input differs; the RSP setup data is the producer.
- H-other-RDRAM: both sampled inputs match, so the width-dependent command
  population comes from another RDRAM table read by the ucode; trace the first
  differing root-relative read before considering any renderer change.

The discriminator is the first normalized byte/hash difference paired with the
same guest source PC and DPC window. Do not add a rendering mitigation.
