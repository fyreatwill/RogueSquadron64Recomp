# NEXT (s5924): why do ~2276 fine-test passes on shape 80323f58 yield only 6 hits?

HYPOTHESIS-ID: g1-mission-progression

s5923: bolts DO enter class-1 spheres (s5901 ratio<1 x13 during poke; s5904 80323f58 all=2278 fine=2276 hret=6).
Hypotheses: (A) fine test passes but findSegmentObjectSphereHit returns t outside [0, 0.34] (A threshold at 0x8003B03C) so caller posts nothing; (B) s5904 'fine' counter counts test entry not hit result (instrument defect); (C) caller discards via a flag/team check after return.
Discriminator: at the function return (funcs_13/16 hook, tools/apply_s5907_hitobj.py is the base) log for obj shape 80323f58 only: fine-test return, out t, A/B floats, then whether the caller posts msg5. Budget scoped per poke window (reset on [plpoke] k change), NOT run-lifetime. Positive control: same log for shape 80330c5c (850 rets must appear).
Outcomes: A -> t units/segment length question (compare dl 1.2-4.6 vs t); B -> fix counter, rerun tally; C -> read caller code after return.
Run: scratch/agent/s5921_poke.sh variant with the new hook.
