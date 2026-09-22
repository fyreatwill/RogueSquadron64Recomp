# M5 s3690 — input-DMA ownership boundary

The first concurrent capture was unevaluable: the retail oracle passed its
whole-RDRAM and target controls, but the port hit the known scheduler startup
crash before phase/source/stage controls. The fixed instrumented build was
rerun without changing the guest path.

The qualified rerun passed the retail whole-RDRAM, descriptor, source-span,
title, hangar, and type-2 controls. The port produced 190 phase rows, 1,024
source rows, 3,784 stage rows, and 8,136 input-DMA events, with no crash or
abort. The new input-DMA event was carried into each source-range witness
before output DMA could replace the thread-local identity.

There were 512 hangar source rows and 2,724 hangar stage rows. Of the 512
source rows, 244 had no same-generation stage row. Every one of those 244
rows joined an input-DMA event with the source's earlier/equal task identity;
none joined a later task identity and none was missing or contradictory.
This selects `H-StaleInputAcrossReuse` over `H-LaterRouteOwnsInput` and
`H-InputDmaKeyStillUnavailable` for the measured class.

This is single-source port ownership evidence; the independent retail run
validates that the same target phases and watched activity were reached. No
guest value, task, RDRAM, DMEM, selector, or output state was rewritten.

ORIGIN: diagnostic input-DMA ownership witness; the input DMA is legitimate
runtime activity, and the change only records its event and identity.
