# NEXT: G3 -- mission 3 flight vs retail angrylion (third biome)
HYPOTHESIS-ID: g3-lvl3-flight

s6748 covered mission 2 flight/bolts; s6749 closed the lvl2 intro duration (H-load: ~3 s retail black lead-in).
Next biome: mission 3 (selected mission byte = 2).
Hypotheses: H-match (terrain, sky, haze, HUD equal: d << same-run median, monotonic); H-biome-tex (a texture/combiner
specific to this biome differs: high-d tiles on surfaces, not edges); H-fog (depth-rising bias); H-desync (non-monotonic).
Steps (one game at a time):
1. python3 tools/g3_eep_patch.py scratch/s6747/oracle.eep scratch/s6750/lvl3.eep --set 0x31=2
2. Retail recon + flight dumps: copy scratch/s6748/retail.sh to scratch/s6750 (D=scratch/s6750/...), EEP=scratch/s6750/lvl3.eep,
   NDUMP=80 DT=0.5 D0=2 ARM=100 (read the 640->512 switch time from a recon run first if it differs from lvl2's 105.9 s).
3. Port: env EEP=scratch/s6750/lvl3.eep PD=../s6750/port SECS=120 CAP0=60 zsh scratch/s6748/port.sh (check the autopilot gate).
4. g3_oracle_match.py --w 512 --bases 690000,620000 --h 446 --win 60,1024 --winx 85,1191 --dec shift; eyeball worst pairs.
Restore/verify: owner save sha (scratch/s6748/owner_save.sha); mupen .eep cmp-equal to scratch/s6747/oracle.eep.
