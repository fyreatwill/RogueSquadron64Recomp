RESUME (s5525): s5524 only landed the ROGUESQ_FORCE_CINE_A0 override in tools/fixup_game_funcs_vendored.py (unbuilt, unrun).
Steps: 1) run fixup_game_funcs.py + cmake build; 2) grep live funcs_*.c for callers of 0x800A5D80 and classify a0 sources; 3) run base arm and env ROGUESQ_FORCE_CINE_A0=1 arm sequentially; positive control: "[cineBody] a0 forced 0 -> 1" appears.
Hypotheses: H1 forced a0 selects a different mission; H2 a0 only indexes cinematics, mission index elsewhere; H3 forcing crashes/no-ops.
HYPOTHESIS-ID: second-distinct-mission-coverage
