# NEXT work unit (s1969) — whole-RDP consumer-side blend/z census

HYPOTHESIS-ID: hangar-hologram-beam-artifact

## What s1968 settled

The corrected `0xD60..r16` walker saw the live hangar triangle stream but
zero valid standard RDP `SETOTHERMODE_L/H` commands. It saw 1,134 parsed
triangles with ordinary `stored=1` writer-attestation control and rejected
six `0xB9/0xBA` header-shaped bytes whose operands violated the standard
32-bit field contract. H1 is therefore not refuted or selected in this
buffer. H2 remains refuted by s1967; H3 remains unavailable to the oracle.

## Single next work unit

Add one regeneration-safe RT64 consumer-side census in
`lib/rt64/src/gbi/rt64_gbi_rdp.cpp`, immediately before the existing
`state->rdp->drawTris(...)` call in `decodeTriangles`. Reuse
`ROGUESQ_LOG_M4_TRI_DUMP` and its cap; gate rows to the hangar VI (`width=512`
and `origin=0x006AB400` or `0x006AB800`), reset the row budget on origin
change, and print the actual triangle screen bounds plus the active RT64
other-mode H/L words and decoded `Z_CMP`, `Z_UPD`, `ZMODE`, `CVG_X_ALPHA`,
`ALPHA_CVG_SEL`, and blender inputs. This is the actual RDP triangle consumer,
not the stale-tail `0xD60` walker. Because this is under `lib/`, run
`./submodule-patches/export.sh` after the edit and commit the refreshed patch
artifacts in the same iteration.

## Competing hypotheses and discriminating measurement

- **H1-consumer-wrong:** a consumer-side triangle whose screen bounds cover
  the beam has incompatible blend/z state, selecting H1.
- **H1-consumer-correct:** the beam-covering consumer triangles have a
  coherent translucent state (`Z_CMP`/`Z_UPD`/coverage/blender fields),
  refuting H1 and leaving H3 as the only remaining explanation available to
  this runtime/oracle pair.
- **H1-consumer-unreached:** the existing DPC writer-attestation control is
  live but `decodeTriangles` emits no hangar consumer rows, proving this is
  not the actual path for the LLE triangle and requiring a different consumer
  hook; it does not select H1 or H3.

**Discriminator:** one build and one established hangar recipe with the DPC
`[m4-tri]` control plus the new consumer rows. A row with bounds in the
beam-cone region and an incompatible mode selects H1; compatible state on all
beam-covering rows refutes H1; zero consumer rows with live DPC triangles
selects the unreached-path outcome. Do not infer a mode from an opcode byte
without its standard fields, and do not add a mitigation.

## Exact run

Build with:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run from `build/` with the s1950 recipe, adding the reused dump flag:

```sh
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M4_TRI_DUMP=1 ROGUESQ_M4_TRI_DUMP_CAP=500 ROGUESQ_M4_Y8000_WIDTH=512 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' zsh ../tools/probe.sh ../scratch/agent/soak_results/s1969_hangar_rdp_state 180 2
```

The known `filterVoiceSampleBlock+220` crash is acceptable only after the
hangar positive control and consumer rows have been captured. If the crash
prevents the consumer rows, record the scope as unevaluable and enqueue the
recipe rather than chasing that known family.

## Do not repeat

- Do not scan `0xD60` for `0xB3`/`0xBE` or accept impossible `0xB9`/`0xBA`
  operands as mode commands.
- Do not rerun the H2 writer-attestation check or the parked M4 `Y=0x8000`
  accumulator question.
- Do not use a stopwatch or cross-run visual A/B; the gate is the hangar VI
  origin and the same-run writer/consumer controls.
