# Regen safety: put the other post-fixup apply scripts into the replay list

HYPOTHESIS-ID: m5-audio-destub-mission-route

s4809: A10 apply now idempotent and in RS64_REPLAY. tools/apply_s4805_m5_a9.py and tools/apply_s4805_ovl2c_mode.py are in no regen stage (grep count 0), so a regen silently drops A9 logs and OVL2C_MODE.
Work unit: make both idempotent (run twice on an unpatched scratch copy, cmp against live tree), add to RS64_REPLAY, then run tools/fixup_game_funcs_vendored.py on a scratch copy end to end (RS64_SKIP_REPLAY unset) and check "[s4648-replay] failures=0" with the new entries.
Discriminator: failures=0 and cmp identical => regen chain preserves A9/A10/OVL2C_MODE; any FAIL names the script to repair.
