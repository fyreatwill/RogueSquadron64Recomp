# NEXT: fold s5757_bit1ctx soak — why does pending-event bit1 (mtm a0=1) get set every mission start?
s5756 non-god result (s5758 entry): hudbit 0 lines (objbool fired = control live), so setHudEnableBit4 is NOT the end path; mtm(a0=1) fires from runInMissionFrame's event table with b7=b64=b65=b6D=0. Bit1 has one writer 0x800B1140 (funcs_30, per-object update right after terrain query jal 0x80067D90; gated only by word 0x8010CA20==0). Same in god and non-god => godmode was not the confound.
Task: grep [bit1ctx] in scratch/agent/m6/s5757_bit1ctx/run.log. Compare terrain (f2) vs y (s1+8), b_BB, gate_CA20 at the first hit and subsequent hits. Control: >=1 [bit1ctx] line.
Hypotheses: H1 terrain query returns garbage (heightmap unloaded) so object thinks it crashed; H2 s1 is legit player ship and bit1 = designed "mission start/spawn" event whose handler mtm(1) is benign, real end is mtm mode 3 from elsewhere; H3 s1 is a non-player object.
Discriminator: terrain value sane (~ y) vs wild; s1 pointer == player object.
HYPOTHESIS-ID: g1-nonhealth-fail
