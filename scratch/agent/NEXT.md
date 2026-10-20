# NEXT: G1 - find how the port selects the mission level and reach a level other than 2
Context: s5695 closed the G2 dialogue request path (lv2 voice handlers fire and reach allocAndConfigureNewVoice). Soaks always land in level 2; level F's init (sayWhoaHim, bool 7) never runs.
Hypotheses: H1 level is chosen by a menu/hangar selection the autopilot never changes; H2 a save-file/memory word picks it (saves/ dir); H3 a forced default in the port.
Discriminator: offline first - grep CURRENT-TRUTH/PORTING-STATE for the level-index global written before lv2_initializeObjectTracking runs, then log it ([lvl]) in one soak with a keyed level-select (or poke) arm; positive control = value reads 2 in the default arm.
HYPOTHESIS-ID: g1-level-select
