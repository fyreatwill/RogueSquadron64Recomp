# NEXT (s7516)
HYPOTHESIS-ID: motor-pak-shape-vs-hardware

First: fold s7515_fl_levels from SOAK-RESULTS if it ran (score 0 -> FL CLOSED 6 levels in CURRENT-TRUTH item 20; 1 -> a live
EEPROM divergence: read scratch/s7515_fl_levels/out.txt BAD lines; 3 -> ctl row missing; 4 -> no [s7515-eep] rows).

Work unit: class FM, Rumble Pak (osMotorInit/Start/Stop, 9 live callers per s7513) and Controller Pak (osPfs* 8, stubbed) shape vs
hardware. Hardware: with no pak, osMotorInit returns PFS_ERR_NOPACK (1) / PFS_ERR_DEVICE (11) for a non-rumble pak; osMotorStart/Stop
on an uninitialised OSPfs return an error; osPfsInitPak with no pak -> PFS_ERR_NOPACK. Read the host stubs (grep osMotor / osPfs in
lib/N64ModernRuntime and src/), list what each returns, then read every game branch on those returns (statically, as s7515 did for
initSaveData). Hypotheses: H-canon (host returns = hardware no-pak / rumble-pak returns) / H-dead (differences only feed unused paths) /
H-live (the game takes a path hardware never takes with the reported pak, e.g. believes a rumble pak exists and retries per frame,
or reports a Controller Pak it cannot read) -> fix to the hardware rule (decide which pak the port reports: SDL rumble = rumble pak).
Measurement: static census + one runtime env ROGUESQ_LOG_PAK_SHAPE=1 (every osMotor*/osPfs* call: args, return, game caller ra) with a
planted ctl row, scorer with synthetic + mutant controls; L4 dd1 + L15 dd8 21:9 via tools/g1e_owner_quiet_arms.zsh (s7515 command in
PORTING-STATE), levels soak queued after.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
