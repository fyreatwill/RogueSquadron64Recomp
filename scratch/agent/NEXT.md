# NEXT: G3 render fidelity, mission 3 flight vs retail angrylion (third biome)
HYPOTHESIS-ID: g3-retail-match-lvl3

Context: hangar-fov thread closed s6838. G3 flight H-match exists for lvl1 (s6744-s6747) and lvl2 (s6748, Barkhesh). Next
biome: mission 3. Recipe = s6748: tools/g3_eep_patch.py scratch/s6748/lvl2.eep-source OUT --set 0x31=2 (re-signs both copies),
retail recon in rs64_oracle (time 1024/512/640/flight transitions), then matched no-input arms (retail 512 dumps over flight,
port window captures), tools/g3_oracle_match.py --w 512 --dec shift with Display-P3->sRGB (s6740), cross-frame control.
Hypotheses: H-match (port flight frames within the lvl1/lvl2 d range of retail, cross-frame control far) vs H-diff (a
biome-specific texture/combiner/fog difference: d outside range, localized region) vs H-route (the save does not select mission
3 in one arm: check the intro biome first).
Discriminator: per-frame d distribution port vs retail over the overlapping flight window, against the shifted-frame control.
H-diff -> crop the region, diff the RDP stream (tools/g3_rdp_frame_match.py) to split game-side vs RT64.
