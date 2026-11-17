# NEXT (s7521)
HYPOTHESIS-ID: rsp-executed-code-bytes-census

First: fold s7520_fq_levels from SOAK-RESULTS if it ran (score 0 -> FQ CLOSED 6 levels in CURRENT-TRUTH item 20; 1 -> read
scratch/s7520_fq_levels/out.txt LIVE rows (class, sym@subsegment; a CODE word = a real run-time code write, name the writer);
3 -> a ctl did not fire on some arm (check [s7520-ctl] lines); 4 -> no [s7520-sum]).

FQ closed the CPU side of "executed bytes vs recompiled image". New class FR = the RSP analogue. RSPRecomp compiled the Factor 5
ucode (main + B + boot + overlays 4/10/12/14/18/1C/20/24/2C) from ROM bytes; the RSP runs whatever DMEM/IMEM bytes the task and the
ucode's own IMEM overlay DMAs bring in from RDRAM. Hypotheses: H-canon (at every SP task start the RDRAM ucode text/data the task
points at equals the ROM bytes RSPRecomp compiled, and every in-ucode IMEM DMA source equals the ROM overlay image), H-dead (some
differ but only in bytes the compiled path never reads, e.g. DMEM data patched per task by design), H-live (the game patches ucode
in RDRAM, or an IMEM DMA pulls bytes RSPRecomp never saw, so the port runs different RSP code).
Instrument: at each SP task start (upstream_compat.cpp task hook), hash RDRAM [ucode, ucode_size] and [ucode_data, ucode_data_size]
against the ROM images (locate by the regen inputs: tools/ucode_regen.sh, factor5*_rsp.toml rom offsets); at each RSP-side SP DMA
into IMEM (the rsp DMA path used by the LLE ucode) compare the source RDRAM bytes with the ROM overlay image the toml compiled.
Ctl: env flips one byte of the ucode text in RDRAM before the Nth task and requires a DIFF row. Runs: L4 dd1 + L15 dd8 21:9 via
tools/g1e_owner_quiet_arms.zsh, then a levels soak. Read docs/F5-UCODE-REFERENCE.md first.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
