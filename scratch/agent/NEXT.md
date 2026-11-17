# NEXT (s7515)
HYPOTHESIS-ID: eeprom-save-shape-vs-hardware

First: fold s7514_fk_levels from SOAK-RESULTS if it ran (score 0 -> FK CLOSED 6 levels in CURRENT-TRUTH item 20; 1 -> a live rate/
monotonicity/clk/gate defect: read scratch/s7514_fk_levels/out.txt for the field; 3 -> ctl rows missing/gate not 1 under ctl;
4 -> no [s7514-time] rows).

Work unit: class FL, EEPROM / save-path shape vs hardware. Live wrappers (RecompiledFuncs): osEepromProbe 1 (initSaveData),
osEepromLongRead 3 (initSaveData, loadOrSaveAllEepromRecords, loadOrSaveEepromRecord), osEepromLongWrite 3 (initSaveData x2,
saveLoadDispatcher); osEepromRead/Write 0. Host side: lib/N64ModernRuntime/librecomp/src/eep.cpp. Hardware rules (libultra +
n64brew): probe returns EEPROM_TYPE_4K (1) or 16K (2) per the cart (RS64 = 4 Kbit? check the ROM header / game's own use of the
probe result); LongRead/LongWrite address is a BLOCK index (8 bytes), nbytes multiple of 8, address+nbytes/8 <= 64 (4K) or 256
(16K), errors return -1 / CONT_NO_RESPONSE_ERROR; LongWrite waits ~15 ms per block on hardware (osEepromLongWrite busy-waits
EEPROM_WAIT); retail return value 0 on success.
Hypotheses: H-canon (every live call's address/length in range for the probed type, return codes = libultra, bytes round-trip) /
H-dead (differences only in paths behind ROGUESQ_NO_SAVE_WRITE or unused types) / H-live (the probe type disagrees with the
size the game indexes, an out-of-range block silently wraps or succeeds where hardware errors, or a return code differs where the
game branches on it) -> fix to the hardware rule.
OWNER SAVE RULE: build/saves is the owner's real save; NEVER clear ROGUESQ_NO_SAVE_WRITE. Measure reads only, plus writes as
logged-and-suppressed calls. A test needing a writable save copies the game to its own folder.
Measurement: static census (args at each jal, game branches on the return), one runtime census env (ROGUESQ_LOG_EEP_SHAPE=1: every
probe/LongRead/LongWrite with address, nbytes, return, first 8 bytes) on L4 dd1 boot->mission and a hangar route, offline scorer
with synthetic + mutant controls and an in-run ctl (ROGUESQ_EEP_SHAPE_CTL: one logged call with a planted out-of-range address
that the scorer must flag).
