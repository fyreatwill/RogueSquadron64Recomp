# NEXT: who fills the cell material-link table 0x80136FCC, and is it radius-bounded?
HYPOTHESIS-ID: g1c-dd8-limit
Closed s6486: fog colour is not the dd4 missing-ground band (magenta control fired at dd1, ~0 at dd4).
H-writer-radius: the link halfwords in 0x80136FCC are written only for cells within a fixed radius of the player (loader/streamer), so widened cells stay empty.
H-writer-static: table is filled once at level load from level data covering a fixed area; dd cannot extend it without data.
Discriminator: find writers of 0x80136FCC (grep recompiled funcs for stores relative to that base, lui 0x8013 / addiu 0x6FCC); log per-frame count of nonzero halfwords in-window at dd1 vs dd4 pinned. Positive control: dd1 count > 0. Same count at dd1/dd4 => static (H-writer-static); larger at dd4 => radius-bounded and a gate exists.
