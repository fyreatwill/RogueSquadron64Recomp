# NEXT work unit (s2087)

HYPOTHESIS-ID: m5-voice-output-base-provenance

## Work unit

Perform one bounded census of the voice-slot `+0x34` field that feeds
`fillSampleStreamRange`'s `a1` at the port-active `0x800903F0` edge. First run
the independent retail control with the whole-RDRAM positive control and a
physical watch over the companion voice array; then enumerate every generated
store/load of the field and reconcile the sites with the companion mapping.
Do not add a port witness, build, or runtime behavior change until the static
census and retail writer control are complete.

## Competing hypotheses and discriminator

- **H-ValidVoiceBase** — `+0x34` is the per-voice output-buffer base; its
  generated writers store valid RDRAM addresses, and retail's writer-PC
  histogram shows the same field being populated during title/hangar.
- **H-ScalarField** — `+0x34` is a scalar or tag in this path, so the
  pointer/range interpretation is wrong and the ASCII-like values are not
  corruption.
- **H-InvalidWriter** — a generated writer or copy populates `+0x34` with a
  non-RDRAM value before the active edge; the callee's pointer/range ABI is
  correct but the upstream value is bad.
- **H-WrongSlotBase** — `s1` at `musyxRenderVoiceSamples` is not the voice
  slot assumed by the companion mapping, so the `+0x34` census is attached to
  the wrong object or stride.

The discriminator is one writer table joined to the independent retail
writer-PC histogram. The table must identify each generated `+0x34` writer,
the source value, the object/register base, and the companion meaning. If all
writers are output-buffer stores and retail writes the same field with valid
RDRAM values, select H-ValidVoiceBase and move the open boundary to a
port-only slot writer/copy. If the mapping identifies a scalar/tag, select
H-ScalarField. If a writer produces the wild/non-RDRAM class, select
H-InvalidWriter. If the caller base or stride does not resolve to the voice
array, select H-WrongSlotBase. A missing retail writer hit is unevaluable
unless the whole-RDRAM control and title `1024 @ 0x00790400` plus hangar
`512 @ 0x006AB400` phases all fire.

## Ground truth and exact commands

Read `tools/oracle/README.md` before driving the oracle. The companion mapping
identifies the voice array as physical `0x1496F8`, stride `0x88`; the `+0x34`
fields occupy the bounded physical span beginning at `0x14972C` and ending
before `0x14B92C` for 64 slots. Run the retail control from the repo root:

```sh
mkdir -p scratch/agent/s2087_oracle
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 65 --watch-write 0x0:0x800000 \
  --watch-write 0x14972C:0x14B92C \
  --pc-hist-watch 1 \
  --watch-pc 0x8009024C:0x80090250 \
  --watch-pc 0x800902CC:0x800902D0 \
  --watch-pc 0x800903F0:0x800903F4 \
  --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2087_oracle/run.log 2>&1
```

The oracle must report the whole-RDRAM control, both target VI phases, the
voice-range writer histogram, and the active retail callee caller PCs before
the table is interpreted. Then enumerate the static sites without reading
large files wholesale:

```sh
rg -n -C 5 '0x800903F0|0x8009024C|0x800902CC|0x8008FFAC|0x8008FAAC|0X34\)|0x34\)' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/main_overlay.txt \
  | head -260
```

No wait, guard, task-field, output-routing, canary, gate, or host behavior
change is authorized. If the static writer table and retail histogram do not
separate the four hypotheses, stop and put the unresolved table here rather
than adding another diagnostic field.
