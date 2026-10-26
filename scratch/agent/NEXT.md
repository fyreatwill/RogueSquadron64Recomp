# Next: G3c(a) static-enumerate projection/fog writers (H-aspect vs H-fade)
HYPOTHESIS-ID: g3c-owner-visual

s6295: terrain radius at 0x80043918 is unchanged in 21:9 flight (19.68-23.94, eff=1) -> H-radius out.
Remaining: H-aspect (widened frustum exposes grid-aligned cell edge) vs H-fade (fog/haze start/end
not scaled with dd/aspect). One bounded unit: grep-enumerate every writer of the fog/haze
start/end (and the s6144 frustum x-widening consumer) in generated code, then compare their values
in one wide run vs retail (single run each, NOT concurrent) plus the contact-sheet edge score.
Outcome map: fog values equal retail and edge present at far x -> H-aspect (cull/extend cells
in x); fog identical but dd>1 edge inside haze gap -> H-fade (scale fog). Do not add mitigation
before naming the writer (iron rule 11).
