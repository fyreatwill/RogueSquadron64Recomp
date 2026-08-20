# NEXT work unit (s1999) — ground-truth and generated-gate reconciliation

HYPOTHESIS-ID: m5-audio-ground-truth

## Single work unit

Reconcile the retail oracle's audio-gate writes with the current generated
output, fixup source, and host M_AUDTASK dispatch. This is one ground-truth
experiment plus static source comparison. Do not build, regenerate, edit
generated code, or change runtime behavior until the result selects an arm.

The target physical addresses are the KSEG0 translations of the generated
guest fields: `0x800A0F50` (audio/display gate), `0x8014998A` (wait countdown),
and `0x8014974C` (second wait flag). The whole-RDRAM watch is the positive
control; a target null is invalid unless the whole-RDRAM control visibly fires.

## Competing hypotheses and discriminating outcomes

- **H-generated-mismatch:** `fixup_game_funcs.py` intends to force-zero the
  `0x8008EC88` tail, but its regex misses the current intervening probe call.
  If current generated output stores `1` and the source fixup does not match,
  generation reconciliation is selected before any audio de-stub.
- **H-legitimate-retail-gate:** the retail writes the gate from the expected
  init/display PCs and values. Matching oracle writer PCs/values, plus the
  same store sites in generated output, proves the `1` is a legitimate guest
  state rather than a port-only shortcut.
- **H-independent-dispatch:** the gate fields are not evidence that the host
  M_AUDTASK path is exercised. If the oracle records gate activity but the
  port's dispatch is only selected by `ROGUESQ_AUDIO_UCODE`, keep gate repair
  and task-format selection as separate work units.
- **H-wait-owner:** the retail countdown/flag writes are absent in the reached
  phases, or come from a different owner than the port's wait loops. That
  selects ownership tracing for the waits and rules out treating their current
  pump/timeout behavior as an audio de-stub explanation.

The discriminator is one table with rows for each target address: oracle
writer PC/value/phase, generated writer/constant, fixup match status, and host
dispatch evidence. Possible outcomes select one of the four hypotheses above;
no target hit with a live whole-RDRAM control is a phase limitation, not proof
of absence.

## Exact commands

First make the capture directory and run the retail oracle once. The whole
RDRAM watch is deliberately capped high enough to retain its positive-control
lines while the three narrow watches preserve target evidence:

```sh
mkdir -p scratch/agent/m5_step1_groundtruth
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 30 \
  --watch-write 0x0:0x800000 --hit-cap 2000000 \
  --watch-write 0xA0F50:0xA0F54 \
  --watch-write 0x14998A:0x14998C \
  --watch-write 0x14974C:0x149750 \
  > scratch/agent/m5_step1_groundtruth/oracle.log 2>&1
```

Then inspect counts and bounded target lines; never dump the whole log:

```sh
grep -c '^\[hit\]' scratch/agent/m5_step1_groundtruth/oracle.log
rg -n '0x00a0f5[0-3]|0x0014998[ab]|0x0014974[cef]' \
  scratch/agent/m5_step1_groundtruth/oracle.log | head -100
rg -n -C 3 '0x800A0F50|0x8014998A|0x8014974C|M_AUDTASK|musyx_stub|factor5_ucode_b' \
  src/main/main.cpp ../N64Recomp/fixup_game_funcs.py \
  ../N64Recomp/RecompiledFuncs/funcs_23.c \
  ../N64Recomp/RecompiledFuncs/funcs_24.c | head -240
```

Positive-control acceptance is `grep` reporting at least one whole-RDRAM hit
and the oracle's normal completion marker. If either is absent, record the
oracle run as invalid and do not infer anything from the narrow watches. If a
target is hit, classify its PC and value from the bounded lines before
deciding whether the fixup pattern or runtime source is authoritative.

## Next decision

Write the completed address table and the selected hypothesis into
`PORTING-STATE.md` and `docs/CURRENT-TRUTH.md`. If H-generated-mismatch is
selected, the following unit may repair the fixup pattern and regenerate in the
documented order. If H-legitimate-retail-gate or H-independent-dispatch is
selected, leave the gate alone and proceed to the smallest host/task-format
validation arm. If H-wait-owner is selected, trace the retail writer before
touching a wait. Every later behavior change still needs its own same-run
positive control, VI phase, soak, and rollback from `docs/M5-AUDIO-PLAN.md`.
