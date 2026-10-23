# NEXT: decide whether lvl1 dark-mesh ground (fb 4000/4500) is a texture defect
HYPOTHESIS-ID: g3-lvl1-mesh-ground
H1 legitimate level geometry (launch/landing deck texture); H2 wrong texture/tmem for terrain tris (port-only defect); H3 FIX_ZERO_SHADE side effect.
Discriminator: in a lvl1 run, dump the ground tris' texture (TMEM/LOADBLOCK source addr+fmt) at the flat-ground frame and render the raw texel bytes; a real grate/mesh texture in ROM => H1, noise/format mismatch => H2. Toggle FIX_ZERO_SHADE within the same run for H3. Positive control: same dump on the hill frame (3500) must show the grass texture. Alternatively get a retail oracle of lvl1 via s5978_retail_flight.sh route (level index 1 only reachable after mission 1).
Otherwise continue G4 soaks.
