# NEXT: menu worker overlap check + close G3 front-end (G3)
HYPOTHESIS-ID: g3-frontend-remaining

Done s6783: OPTIONS sub-screens + ERASE GAME match retail at RDP level (tools/g3_rdp_frame_match.py, tools/g3_menu_pair.sh).
Unit (one build, one paired run set):
1. Add ROGUESQ_XTRACE_MEM marks to tools/fixup_rand_trace.py (same pattern as the s6781 menu worker marks, line ~130):
   0x800C5880 (tickSongAssetLoadWorker completion send, jal 0x80006F78) and 0x800C3B4C (menuSubtype02Handler receive,
   after the recv returns: dump v0). Regen order make_elf -> N64Recomp -> fixup_game_funcs -> cmake (CLAUDE.md).
   Positive control: the existing 0x800B380C/0x800B4004 marks must fire on SELECT GAME in the same run.
2. Port: g3_menu_pair.sh style route title -> SELECT GAME -> SELECT LEVEL -> craft select (song loads happen here) with
   ROGUESQ_XTRACE_MEM=800B380C:6:0:8,800B4004:3:0:8,800C5880:6:0:8,800C3B4C:3:0:8 (check spec format in fixup_rand_trace).
   Retail: oracle --exec-trace 0x800C5880 + 0x800B380C (+ -also 0x800C3B4C/0x800B4004), same presses.
3. While the RDP recorders are cheap: RDP-compare the title START/OPTIONS menu and OPTIONS top level
   (PP="17:down,19:a" hold), tools/g3_rdp_frame_match.py with a cross-screen control.
Hypotheses: H-disjoint (the two workers are never pending together: s6782 residual dead, G3 front-end closes) vs
H-overlap (a 0x800B4004 receive sees a song-worker message or 0x800C3B4C sees a format-worker message, in either arm:
then name which arm and whether the payload is dereferenced). Title/OPTIONS: H-match (exact/median-0 like s6783) vs
H-diff (items absent/extra: find the writer).
After this: G3 front-end is closed; take the next ladder rung per ITERATION.md 3c (G3 hangar artifacts list in
CURRENT-TRUTH, or G1d owner judgement items).
