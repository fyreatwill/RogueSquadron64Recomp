# NEXT: run the lldb hp/lives write-watch on the s5738 ROUTE (level-select AP_OVERRIDE keys, MISSION_RE=62BD00), not the plain route
s5742 showed the death-arm env alone does not kill on the plain route (0 hp/lives writes, 241 s). s5738 deaths came with the level-select key stream + saves_s4224_aside copy.
Build scratch/agent/soak_queue/s5743_hpwatch_lvsel.sh = s5738_snapa.sh preamble (save copy, EARLY/FL/AP_OVERRIDE, XENV incl LOG_OBJBOOL/HUDBIT) but with the lldb watch harness from scratch/agent/s5739_hpwatch.sh (MISSION_RE 62BD00 instead of 690400 gating). Hold >=300 s.
Hypotheses: (H1) a game routine reacting to autopilot held-stick writes kills the craft; (H2) mission 62BD00 has a hazard (terrain/enemy) the plain mission lacks; (H3) port defect in held-input path.
Discriminator: top frame/PC at the hp->0 write (wp2) and lives decrement (wp3). Positive control: a death must occur in the run ([snap] death#1 in log) or the null is void.
HYPOTHESIS-ID: g1-gameover-cause
Caveat: s5739_hpwatch.sh still gates on origin 0x006AB400 (hangar) before mission; if att fails 'nohangar', the lvsel route skips the hangar - relax that gate.
