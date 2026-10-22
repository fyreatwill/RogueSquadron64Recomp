# NEXT (s5898): why do player bolts travel <3 u? log vel/dt/age per bolt life
Context (s5897): 94% of 19072 bolt lives move <1 u; all 60 hits within 3.2 u of life start; survivors are on-axis at 12-24 u. H-aim superseded by H-range.
Competing: (a) bolt per-step velocity tiny (|dir| 0.09-2.1 per test) because dt/time-scale is wrong in the port; (b) lifetime/age despawn too short (timer in wrong units); (c) bolt removed by an intervening object/terrain test; (d) tracker artifact (stationary idle pool slots dominate <1 u bin).
Discriminator: in rs5897_track also log bolt object vel/age fields (dump 0x100 bytes of proj at life start and at life end for first 20 lives with maxdist>=1, plus a control: lives with hit); and exclude lives with n==1 from histogram (artifact test). Find the bolt update fn via grep of the proj ptr 0x8035xx1c writers (watch the pos field). Outcome (a)/(b): vel or age field wrong -> trace writer of dt; (c): find the remover; (d): redo histogram.
Recipe: scratch/agent/s5897_life.sh.
HYPOTHESIS-ID: g1-mission-progression
