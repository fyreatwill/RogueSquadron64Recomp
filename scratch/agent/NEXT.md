# NEXT work unit (s2455) — ground live port second-range provenance

HYPOTHESIS-ID: m5-port-second-range-provenance

## Work unit

Use the retail oracle and the existing phase-gated port witnesses in one
matched investigation to determine whether the port's second-range execution
is the `allocateSongChannelArray/0x8008F2CC` path, another direct generated
`rs_memset` caller, or a dynamic lookup path. Do not change behavior or add a
diagnostic field.

## Competing hypotheses and discriminator

- H-PortF2CC: the live port rows correspond to the generated
  `0x8008F2CC -> rs_memset -> after_6` path.
- H-PortOtherStatic: a different direct generated `rs_memset` caller reaches
  the second range.
- H-PortDynamic: a runtime lookup/dispatcher path reaches `rs_memset`.

The discriminator is one phase-gated joined table with retail
`PREVIOUS_PC`/`$ra` at `0x800078EC` and port `m5-static-rsmemset` plus
`m5-second-exec` caller/continuation evidence. Retail `PREVIOUS_PC=0x8002BEEC`
with `ra=0x8002BEF4`, joined to the known `0x8008F2CC` setup, and port rows
showing `callsite=0x8008F2CC` select H-PortF2CC. A different complete port
callsite selects H-PortOtherStatic. A `get_function` target row tied to the
stores, with no static caller row, selects H-PortDynamic. Missing positive
controls or unmatched phases are non-results.

## Exact commands

1. Arm the retail positive control and target PC in one run:

   `tools/oracle/build/rs64_oracle --core "$ORACLE_CORE" --rom "$RETAIL_ROM" --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 120 --watch-write 0x0:0x800000 --watch-pc 0x800078EC --pc-phase-log 0x6ab400 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start`

   Require `[gpr-ctl]`, whole-RDRAM hits, the hangar origin, and target-PC
   rows before using the retail attribution.

2. In one qualified port run from `build/`, enable the already-built
   `ROGUESQ_LOG_M5_STATIC_CALLS=1` and `ROGUESQ_LOG_M5_SECOND_EXEC=1` witnesses,
   capture stdout/stderr to a non-dot-prefixed path, and SIGKILL the process
   after the same 120-second phase window. Join rows by phase/origin and retain
   only the 512 / `0x006AB400` bucket.

3. Compare the complete bounded caller table against the audit at
   `scratch/agent/s2454_m5_dispatcher_replacement/audit.md`; do not interpret
   a null without both controls.
