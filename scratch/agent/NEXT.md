# NEXT (s7476)
HYPOTHESIS-ID: guest-heap-data-integrity

Class ED root cause: who calls reapplyDisplayMode(a1=1) at boot t~0.94, and is count=1 legitimate?
s7475 found: reapplyAudioConfig (0x80091C88, via reapplyDisplayMode 0x8008EB5C which stores a1 to 0x80141AD0) re-allocates the
MusyX voice array (base 0x801496F8, stride 0x88, count u16 0x80149700) with count=1, while voice index 1 stays live
(musyxSetVoicePitchBend 0x800923B8, beginVoiceFadeRelease 0x800924C4 write voice[1], past the block). Then count=16 at t=5.24.
Hypotheses:
- H-port-reapply: retail never calls reapplyDisplayMode at boot (s4711 oracle, single-source); the port reaches it through a
  port-specific path (display-mode / B40 gate 0x800A0F50 stubs, fixup_game_funcs_vendored.py ~8282). Fix: the port path.
- H-retail-count1: retail does call it with count 1 (oracle undercoverage); then it's a retail bug (voice[1] in the slack +
  next block) and the fix is a capacity floor (allocate max(count, live voices)) behind an =0 switch.
- H-stale-index: count=1 is legitimate, but the voice index comes from a stale song/channel record that should have been reset
  on re-init (name the source of a0=1 in musyxSetVoicePitchBend's caller).
Discriminating measurement (one build, one boot, ~60 s):
1. Name the caller chain of reapplyDisplayMode at t~0.94: host backtrace (backtrace() + dladdr) at the
   [s4712-mixer-callsite] name=reapplyAudioConfig print (find it in fixup_game_funcs_vendored.py; add a frame dump under
   ROGUESQ_S7476_BT=1), plus the guest caller of musyxSetVoicePitchBend(a0=1) via the s7475 slack-store row
   (add a host backtrace on the first slack-store row).
2. Oracle (tools/oracle/README.md): watch physical 0x149700 (voice count halfword) and 0x141AD0 writes in retail boot+attract
   80 s, with a whole-RDRAM positive control. Count=1 written in retail -> H-retail-count1; never -> H-port-reapply.
3. Then fix + re-run: env NAME=s7476_boot zsh tools/s7475_boot_ab.zsh (A5 arm must reach cineBody once voice[1] is in bounds),
   then the flight sweep: env NAME=s7476_canary LV="4:4 7:4 12:4 15:8" zsh tools/s7475_canary_recipe.zsh (FILL=0 + STORE_DIAG).
Note: STORE_DIAG makes the game slower; if flight arms fail to reach initMission, raise HOLD or queue as a soak.
