# NEXT: lvl9 port HUD + engine-glow drop (ticks 292-458), retail draws them
HYPOTHESIS-ID: g3-lvl9-hud-drop

s6761 datum (single-source): dt-pinned lvl9, sim identical to retail for 2216 ticks, but port window captures show no
HUD (radar, ship icon, reticle) and no engine glows for port ticks 292-458 (86.5-92.1 s), while retail fb dumps at
ticks 331 and 400 draw both. Also port-off ticks 2054-2208 (no retail sample there). Sheet: scratch/s6761/hudgap_sheet.png,
scratch/s6761/match/worst0_vi7870_n8782.png. Tool: tools/g3_hud_presence.py SDIR (needs snap.txt + match.txt).
On lvl7/lvl8 the port HUD-off windows coincided with retail HUD-off (scripted), so the tool has a same-method control.

Hypotheses:
- H-gate: the game itself skips the HUD/glow draw in the port (a guest flag/timer we do not log differs; e.g. a
  render-pacing or audio-clocked flag such as a voice line / comm message timer).
- H-gfx: the game builds and submits the HUD DL, but the port's RSP LLE / RT64 / present path does not show it
  (dropped task, wrong framebuffer presented, overlay pass skipped).
- H-retail-sample: retail also hides the HUD in a shorter/shifted window and the 2 retail dumps missed it (would need
  the retail window to exclude both t331 and t400: check with denser retail dumps).
Discriminator, ONE build/run pair (scratch/s6762):
1. Reproduce: rerun scratch/s6761/port.sh (PD=port2, SECS=110) and confirm the gap at the same ticks (deterministic?).
2. In the same port run, count per gfx task the HUD submission: log RDP texrect count (HUD is texrects) and
   G_SETOTHERMODE/overlay markers per frame via the existing dpc_bridge rect logging, keyed to VI. If HUD texrects are
   in the RDP stream during the gap -> H-gfx (RT64/present). If absent -> follow the game side: find the HUD draw entry
   (grep tools/rename maps for hud/radar draw functions) and exec-trace it in both arms over ticks 280-470 (H-gate).
3. Retail: rerun with dense fb dumps (NDUMP=48, FARM such that dumps fall every ~60 VI in vi 7700-8300) to settle
   H-retail-sample.
Then resume G3 sim match missions 10.. (eep +0x31=9, ...).
