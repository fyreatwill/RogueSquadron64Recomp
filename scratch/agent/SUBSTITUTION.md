The planned clear-edge capture could not run because neither same-build pair
was route-valid in both arms. This iteration's evidence is the generated
status and logs in `scratch/agent/s2401_identity_edges/`: the 75-second pair
left Arm A at 640 and produced no 1024 target-origin row; the repaired
120-second pair again left Arm A at 640, while Arm B crashed at guest PC
`0x8000B650`. Both retries emitted the required lifecycle activation control,
so this is a route failure rather than an instrument-control failure.

The single experiment that would refute this explanation is a same-build,
concurrent two-arm run with the route-validity driver repaired so both arms
emit activation and 1024 target-origin controls; only then can the identity
null be interpreted.
