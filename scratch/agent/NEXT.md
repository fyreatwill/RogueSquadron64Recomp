# NEXT work unit — ground-truth the field348 owner slot

HYPOTHESIS-ID: m5-image-stage3-destination

Run one retail-oracle-only capture watching physical slot `0x149764:0x149768`,
with the whole-RDRAM positive control, title/hangar phase gates, and the
existing `0x1935E0` post-value control. Do not add port probes or repeat the
invalid paired recipe until this slot contract is known.

Competing hypotheses:

- `H-PortStage3Field348ProducerGap`: retail writes a different owner-slot value.
- `H-PortStage3DownstreamGap`: retail and port store the same pointer before the clear.
- `H-PortStage3OwnerAbsent`: retail does not use this slot in the target phases.

Discriminator: whole-RDRAM, title/hangar, and retail `0x1935E0` controls must
fire in the same run. A phase-qualified retail write to `0x149764` with the
same values seen by the port selects a downstream/consumer gap; a different
value selects a caller-contract gap; an absent owner-slot write selects the
owner-slot hypothesis. A zero result without all controls is unevaluable.

Command:

    mkdir -p scratch/agent/s3402_retail_field348_owner
    env tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 120 --watch-write 0x0:0x800000 --watch-write 0x149764:0x149768 --watch-write 0x1935E0:0x1935F0 --pc-hist-watch 1 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 --post-value-watch 1 --post-value-pc 0x800078EC --post-value-pc-detail --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s3402_retail_field348_owner/oracle.log 2>&1

Use SIGKILL-only cleanup; retain the oracle positive-control and phase lines.
