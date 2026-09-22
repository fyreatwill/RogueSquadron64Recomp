# M5 s3687 — absent-source DMA owner join

The qualified concurrent capture used the retail oracle and the port's
real-audio Factor 5 arm. Retail whole-RDRAM, descriptor, source-span, title,
hangar, and type-2 task controls fired. The port reached VI 1024 at 14.3 s and
VI 512 at 23.6 s, and its source-hook, ABI, DMA, source, and stage controls
fired without a crash or abort.

The port recorded 512 hangar source rows, 2,750 hangar stage rows, and 1,368
hangar DMA rows. Of 260 source rows without a same-generation stage row, all
had a later same-pointer stage, but the DMA record exposed only
`data_ptr=0x80171E70`, `data_size`, and its own source hash. It carried no
source event, task generation, route ordinal, or route row. The source-span
hash and DMA-task hash are different domains, so hash equality is not a valid
join key. Runtime log order is also not a cross-thread ownership key.

Therefore the capture cannot distinguish later-route ownership from stale
input carried across pointer reuse. It selects `H-DmaJoinUnavailable` at the
current instrumentation boundary; the earlier-route classification from the
first classifier was discarded after the hash-key mistake was corrected. This
is single-source port evidence for the ownership limitation; retail supplies
the independent reachability and watched-activity controls.

No guest value was skipped, rewritten, or guarded. The next discriminator is
to add a stable generation/route/event key to the DMA row at the same handoff
that emits it, then repeat the same qualified capture.
