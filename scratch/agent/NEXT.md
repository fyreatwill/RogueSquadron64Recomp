# Next work unit: classify route sequencing for absent-source later stages

HYPOTHESIS-ID: m5-audio-source-ownership

S3685 selected `H-AbsentPublicationGap`: all 236 hangar source rows lacking a
same-generation stage row had task pointer `0x80171E70` and a later stage row
with that pointer and a greater generation. The next unit must distinguish a
same-route publication delay from a later-route handoff/reuse.

Competing hypotheses:

- H-SameRoutePublicationLag: the later stage row retains the source row's
  route ordinal/row, so the gap is publication timing within one route.
- H-LaterRouteReuse: the later stage row has a greater route ordinal/row, so
  the source was associated with an earlier route and the pointer was reused.
- H-NoStableRouteJoin: route identity is absent or contradictory even though
  generation and pointer match.

Discriminating measurement: retain every absent source row's event, generation,
route ordinal/row, pointer, and DMA hash; find the first later stage row with
the same pointer and greater generation, then classify exact route, later route,
or missing/contradictory route. A complete route match selects
H-SameRoutePublicationLag; a later route selects H-LaterRouteReuse; missing
route identity selects H-NoStableRouteJoin. Require the same positive controls:
retail whole-RDRAM, descriptor, source-span, title, hangar, and type-2 controls
plus port phase/source-hook/ABI/DMA/source/stage controls.

Before running:

    ./submodule-patches/export.sh
    cmake --build build -j8
    env zsh scratch/agent/run_s3686_m5_absent_route_join.sh

Use one qualified concurrent capture, SIGKILL cleanup, and do not alter guest
state or add a mitigation. The new classifier must report counts for all three
classes and must not use the ABI publication counter unless it has a stable
join key.
