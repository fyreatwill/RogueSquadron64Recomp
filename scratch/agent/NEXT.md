# Next work unit: classify retail nonzero source-span writers

HYPOTHESIS-ID: m5-audio-retail-nonzero-writer-identity

s3819 qualified retail at hangar and showed that `0x800078EC` is a legitimate
zero-valued scalar writer, but the final `0x1798B0..0x179A48` snapshot still
has 12 nonzero bytes. The next unit is one independent oracle run that maps
those bytes to their scalar writer PCs and values.

Competing hypotheses and discriminator:

- H1: the 12 nonzero bytes are transient/intermediate stores later erased by
  zero stores, so the final source state is still retail-zero-compatible.
- H2: one or more non-`0x800078EC` PCs make the final nonzero stores, so the
  port clear/fill is missing a retail producer or later writer.
- H3: the nonzero bytes cannot be joined to a qualified hangar-phase scalar
  writer, leaving the boundary unevaluable.

The discriminator is one same recipe with whole-RDRAM control first, exact
source-span watch second, hangar phase `0x006AB400`/512, `--post-value-watch 1`,
`--post-value-pc` for every phase histogram PC (`0x8001E2C0`, `0x80007670`,
`0x8001FACC`, `0x8001FADC`, `0x8001FAE4`, `0x8001FAEC`, `0x8001FAF0`,
`0x8001FAF8`, `0x8001FB10`, `0x8001FB14`, `0x8001FBE4`, `0x8001FD2C`,
`0x800078EC`), plus `--post-value-pc-detail`. H1 requires final snapshot
zero/nonzero bytes to be explained only by intermediate stores; H2 requires a
nonzero scalar sample from another PC at a final-source address; H3 requires
positive controls and hangar phase but no qualified scalar attribution.

Exact command shape:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --watch-write 0x0:0x800000 --watch-write 0x1798B0:0x179A48 --hit-cap 20 --detail-watch 1 --pc-hist-watch 1 --pc-hist-phase 0x6AB400:512 --post-value-watch 1 --post-value-pc 0x8001E2C0,0x80007670,0x8001FACC,0x8001FADC,0x8001FAE4,0x8001FAEC,0x8001FAF0,0x8001FAF8,0x8001FB10,0x8001FB14,0x8001FBE4,0x8001FD2C,0x800078EC --post-value-pc-detail --vi-trace

Capture at `scratch/agent/s3820_m5_retail_nonzero_writer/`; inspect only bounded
summary lines and retain the whole-RDRAM positive-control count.
