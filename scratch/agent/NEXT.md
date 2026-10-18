# Next work unit: rerun the s5370 path census until it reaches hangar and mission
HYPOTHESIS-ID: patcheslib-shadowed
s5370: tools/apply_s5370_path_census.py built; title window shows ent=12288 slot0=0 g2=g3=0 (cached slot 0x801163B0 never empty).
Unit: `zsh scratch/patchq/ab/run_a5370.sh` (single run, keys via winctl; run 2 stalled before hangar, run 1 before title) and read `[a5370]` lines + a5370.keys. Outcomes: mission reached and slot0=0 -> close thread (walk guards dead route-wide, stop guarding); slot0>0 and g2>0 -> read g2bad/g3bad, name the writer; route fails again -> use the soak queue (copy done/s4964_mission_image_*.sh with the census env) instead of babysitting.
