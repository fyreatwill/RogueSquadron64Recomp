# M5 s3685 — generation-absent source/publication join

The qualified concurrent capture passed the retail whole-RDRAM, descriptor,
source-span, title, hangar, and type-2 controls. The port reached both target
phases and emitted the source, stage, ABI, and DMA controls without a crash or
abort. The initial run crashed before phase controls; the same recipe was
rerun after fixing the census parser, and only the fixed run is used here.

The hangar source census recorded 512 input-DMA rows. Of these, 236 lacked a
same-generation stage row. Every absent row used task pointer `0x80171E70`.
All 236 had a later stage row with the same task pointer and a greater task
generation; zero remained without a later same-pointer stage. The ABI
publication log did not expose a matching later publication key, so that
secondary counter is unevaluable rather than evidence against publication.

This selects `H-AbsentPublicationGap` over `H-AbsentNoStageConsumer` for the
measured minority: the source rows are later represented by same-pointer
stage generations outside the immediate generation join. It does not yet
show whether the gap is route sequencing, publication retention, or a
different input-DMA owner. The result is single-source port evidence for the
later-stage relation; retail supplies independent reachability and controls.

ORIGIN: diagnostic source/stage publication join; no mitigation or guest-state rewrite.
