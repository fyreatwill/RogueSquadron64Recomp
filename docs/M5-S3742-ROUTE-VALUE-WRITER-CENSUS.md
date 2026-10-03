# M5 session 3742 — route-value writer census

The independent retail oracle was run before the port build. Its whole-RDRAM
watch fired, its route-PC watch fired at `0x80019CD8` and `0x8000C628`, and a
targeted write watch around physical `0x128C90..0x128D00` fired in the title
phase. The retail watch included a writer at `0x8002BD58`; the oracle run did
not reach the port's qualified hangar phase, so this is title-only retail
ground truth.

The port capture used the real-audio and silent arms in one build, with the
same route candidate/prepare/handoff logs and a store hook installed in all
generated translation-unit helpers. Both arms passed the hook's positive
control, reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and
had no crash or abort marker before the planned SIGKILL.

The route-state-span hook recorded 512 rows in each arm across the target
phases. Every row was a zero-valued byte or word store at the neighboring
fields `0x80128C80/84` and `0x80128CE0/E4`, from PCs `0x8001A06C/74` and
`0x8001C21C/24`. It recorded no nonzero store and no store to the exact
route-value fields used by the qualified route (`0x80128CD0` and the byte
field at `0x80128C92`). The qualified route still reported zero fields at
`0x80019CD8` and zero arguments at the `0x8000C628` handoff; the real arm's
source DMA remained zero while the silent arm emitted no source rows.

This selects `H-EarlierWriterAbsent` for the measured scalar-store class and
rules out `H-EarlierWriterClears` for that class: no earlier nonzero writer was
observed. It does not yet distinguish whether the exact route fields are
populated by an uninstrumented non-scalar operation or whether they are
control metadata unrelated to the image source, so `H-RouteStateNotSource`
remains open. The neighboring zero writers are legitimate state writes; no
mitigation or suppression was added.

Evidence: `scratch/agent/s3742_oracle_groundtruth/` and
`scratch/agent/s3742_m5_route_writer_census/real4.log` plus `silent4.log`.
