# M5 s3686 — absent-source route sequencing

The qualified concurrent capture passed the retail whole-RDRAM, descriptor,
source-span, title, hangar, and type-2 controls. The port reached both target
phases and emitted source, stage, ABI, and DMA controls without a crash or
abort. It recorded 512 hangar source rows and 2,822 hangar stage rows.

The classifier excluded source rows with a same-generation stage row, then
selected the first later stage with the same task pointer and a greater
generation. It found 244 absent-generation rows: 0 same-route matches,
244 later-route matches, and 0 contradictory or missing-route matches. The
later rows retained `0x80171E70` but advanced the route ordinal/row (for
example source route `535/9`, generation `1276`, followed by stage route
`536/10`, generation `1278`). Source event/row, DMA range, length, and source
hash were retained in the report.

This selects `H-LaterRouteReuse` over `H-SameRoutePublicationLag` and
`H-NoStableRouteJoin` for the measured absent-source population. The result
supports pointer reuse across route handoffs rather than a same-route
publication delay. It does not yet establish whether the input DMA belongs
to the later task object or whether the source payload is stale at the DMA
boundary. It is single-source port evidence; the retail run supplies the
independent reachability and positive controls.

ORIGIN: diagnostic source/stage route classifier; no mitigation or guest-state rewrite.
