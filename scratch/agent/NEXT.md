# Next work unit: restore key delivery to the game (M6 blocker)
HYPOTHESIS-ID: m6-mission-endurance

s5414: all prior "mission holds" were attract loop. Recipe now fails (ATTRACT-ONLY) without hangar 0x6AB400.
Do: re-read CURRENT-TRUTH s5393/s5394 key-delivery notes; check CGSSession lock, no crash modal on screen, winctl activate/key positive control (e.g. title -> a visible phase change on key). Hypotheses: (a) window not focused / modal, (b) winctl keycodes wrong for SDL, (c) game ignores keys in attract unless pad init. Discriminator: run with keys and see whether origin 0x6AB400 appears; compare with an in-run SDL key log. Then re-enqueue via m6_mission_tmpl.sh.in.
