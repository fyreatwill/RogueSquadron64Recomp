# M5 s3679 — task handoff thread join

The qualified concurrent capture used the retail oracle positive controls and
the port's title, hangar, source, phase, ABI, and stage controls. The port
reported 1,024 source-range input rows and 1,254 stage-2 rows. Every stage-2
row carried `handoff_thread=1,event_thread=1`; the thread-key control therefore
fired and showed no cross-thread split in this run.

The previous generation result still applies: generation mismatches dominate
the stage rows, while route drift remains present. Combining that result with
the new thread key selects `H-SameThreadPublicationLag` for this capture over
`H-CrossThreadOwnership`. It does not prove the publication mechanism: the
same-thread result is port-only, and a thread-local task pointer or route
record may still be stale when source/stage callbacks run.

No guest value was skipped, rewritten, or guarded. The oracle whole-RDRAM,
descriptor, title, hangar, and type-2 task controls all fired.
