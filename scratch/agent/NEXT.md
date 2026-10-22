# NEXT (s5883): fire kills class-2 objective descs -> get(2)=3 lose. Can fire be aimed so class-1 (21 needed) die without class-2 (3 = lose)?
Context (s5882): fire x2 reproduce get(1) 0->5 then get(2) 1,2,3 -> mission reset; nofire never loses. Win needs get(1)>=21 or get(10)>=6.
Work: log the class-2 desc id + killer message/source at each get(2) increment (descs 0x80319e5c/cce/a9c), and what get(2) increments map to (handler 80065980 desc+0x38/+0x48). Positive control: get(2) steps must appear in fire run. Hypotheses: (a) held-fire A auto-targets nearest incl. class-2 (friendly/escort) objects; (b) class-2 die from enemy fire only when player is near; (c) class-2 die by timer once class-1 count passes some value.
HYPOTHESIS-ID: g1-mission-progression
