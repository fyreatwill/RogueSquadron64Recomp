# NEXT: G3 in-flight retail match for a mission beyond lvl1/lvl2
HYPOTHESIS-ID: g3-flight-lvl3plus

State: s6799 closed g3-flight-thinline (lvl1 thin lines = retail-faithful far-terrain slivers at the horizon; retail
stream carries them, angrylion draws the port's exact edge words as lines). Retail-vs-port in-flight matches exist for
lvl1 and lvl2 only (s6744-s6748, tools/g3_oracle_match.py).

Step 1 (boring first): get the retail oracle into a later mission without playing it.
- The owner save is a 512-byte EEPROM image (scratch/s6744/port1/owner_save_backup.bin; 4 Kbit EEPROM). rs64_oracle
  starts the core with configdir/datadir (tools/oracle/rs64_oracle.c:3883-3901, 4183); mupen writes saves under the
  Core section's SaveSRAMPath (read it at :4197). Put the owner save there as `<ROM goodname>.eep` (mupen pads to 2 KB
  for 16K; 4K EEPROM = 512 B), boot the oracle, and check the SELECT LEVEL screen shows the unlocked missions
  (fb-dump with angrylion as in scratch/s6744/retail_flight.sh). Positive control: the same boot without the .eep must
  show only mission 1.
- Then a press schedule to a mission the owner save has unlocked (lvl3 or later), fb-dumps every 0.5 s in flight.
Step 2: port arm with the same level via the forced route (ROGUESQ_FORCE_SAVE_MISSION=N ROGUESQ_FORCE_UNLOCK=N
ROGUESQ_NO_SAVE_WRITE=1, menus.sh pattern), window caps; run tools/g3_oracle_match.py (Display-P3 -> sRGB, --dec shift).
Outcomes: H-match (port frame distances within the same-run cross-time control) -> lvl N matched; port-only element ->
name it with tools/g3_sliver_scan.py / g3_rdp_frame_match.py on RDP dumps of both arms.
If the .eep route fails (core ignores it): use --state save/load (rs64_oracle.c:3670) only if a state can be made;
otherwise report what blocked it and take the next G3 item.
