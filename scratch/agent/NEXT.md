# NEXT work unit — same-build A/B: request status versus completion-wins

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3302 selected `H-Ed0ClearsThenE70`: the final
`19F50` sees 89F=2, returned F64 reaches `19F6C-post`
with 89F=0, then the next type-1 start / type-2 yield is
followed by `19E70-post` restoring one and the first
`19E80F`. The clear is sound; the named writer is the
scheduler's yield-complete arm.

Independent retail evidence (s3296/s3298/s3301) has no
yield publication or E70 in the viewer: type-1 completion
reaches 19FE4 before type-2. Port source has a contract
gap: `osSpTaskYield_recomp` records only a request and the
runtime never interrupts a task, yet `osSpTaskYielded`
returns that request as if it were a yielded completion.
The weak `osSpTaskStartGo_recomp` clears the request, but
the linked strong override in `upstream_compat.cpp`
shadows it without the clear. This is single-source static
scope until the A/B runs.

## Competing hypotheses

- `H-FalseYieldStatus`: the request-only status is the
  causal divergence. A completion-wins diagnostic arm
  returns zero for this non-interrupting runtime, takes
  19E60 instead of 19E70, restores 19ED0/19F1C/19FE4,
  returns from submit's E0B4, and advances the viewer.
- `H-StatusOnly`: the arm changes E70 to E60 but the
  completion/message ordering still leaves 89C busy or
  submit blocked, so a real completion lifecycle edge is
  additionally missing.
- `H-YieldStatusNotCausal`: baseline and candidate retain
  the same E70/19E80F loop or the candidate changes status
  without any restored scheduler/send progress.
- `H-CoverageInvalid`: either arm misses its env-arm row,
  `640 @ 0x0066A500`, viewer entry, SP completion control,
  SENT n=3, or the scheduler probes.

## Discriminator

One build containing both arms, then two concurrent,
phase-gated runs. Baseline must reproduce E70 → 19E80F.
Candidate E60 plus restored 19ED0/19F1C/19FE4 and submit
return selects `H-FalseYieldStatus`; E60 without those
downstream edges selects `H-StatusOnly`; unchanged status
or no restored edges selects `H-YieldStatusNotCausal`.
Title 1024 or viewer return is a stronger downstream
signal, not a substitute for the joined scheduler row.

ORIGIN: `osSpTaskYield_recomp` legitimately writes the
request bit. The value is not a legitimate actual-yield
result because the current runtime does not interrupt or
resume tasks. Keep the candidate env-gated until the A/B
names the required lifecycle edge. No M5 Step 3.

## Exact commands

Add one env-gated diagnostic arm in
`lib/N64ModernRuntime/librecomp/src/sp.cpp`, e.g.
`ROGUESQ_SP_YIELDED_COMPLETION_WINS=1`, that logs request
and returned status and returns zero from
`osSpTaskYielded_recomp`; baseline retains current request
status. This is a discriminator, not the final lifecycle
implementation. Export the lib patch in the same
iteration. Keep s3288–s3302 probes and enable SP/event
wiring controls. Write one driver that launches both arms
concurrently, waits for phase predicates (not elapsed-time
comparison), SIGKILLs both, and emits a joined verdict.

```
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
  cmake --build build --config Debug --target RogueSquadron64Recomp
./submodule-patches/export.sh
# driver launches baseline + ROGUESQ_SP_YIELDED_COMPLETION_WINS=1
# from build/, with ROM present; both arms use SIGKILL
```

Log: `scratch/agent/s3303_yield_status_ab.md` plus both
captured run logs and the joined verdict.
