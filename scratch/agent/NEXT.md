# NEXT: classify the 2-16 u one-tick flight-camera steps seen in s7120 (both arms), offline first
HYPOTHESIS-ID: fps60-cam-step
Context (s7120): s7119_hop --lag on scratch/s7115/push_{m,n,o,p}.txt finds 21 >0.5 u jerk events in open flight (no need, no lift in the
window): t/t+1 pairs, 2.0-16.3 u, >= 17 ticks after any lift. These are single-tick steps of the presented eye Y. If the owner sees them,
they are hops far bigger than anything the lift does.
Hypotheses:
  H-cut: a legitimate camera cut (respawn, mode change, cutscene/pause camera, debrief): X and Z also jump, cam id or phase changes nearby,
         and retail 30 fps runs show the same steps.
  H-snap: an FPS60 camera snap in steady flight: only Y (or the chase offset) steps, the craft position is smooth, and the steps are absent
         at FPS60=0.
  H-log: a parse or join artefact (an rx line paired with the wrong nl, a cam id switch): the steps vanish when rx is joined by m.
Discriminator (offline, no build): for each event m, print 6 ticks of the rx pos x,y,z, the craft position (if the push log carries it;
  grep the line types first: `cut -c1-3 push_n.txt | sort | uniq -c`), cam id, and the nearest losscan/phase marker. Then grep the m in sh_X.txt
  and the run's VI-phase log for a scene change. Positive control: --inject at a known tick must show up as a Y-only step.
If H-snap survives: one game pair (FPS60=1 vs 0, same L6 recipe, no lift) counting the steps per 1e3 ticks.
