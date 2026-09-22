# Next work unit: resolve the empty retail field table

HYPOTHESIS-ID: m5-retail-guest-field-capture

Session 3721 showed that `0x80094648` executed 128 times in the qualified
hangar route but produced zero `pc-field-dump` rows. Its execution hits were
at origin `0x006AB800`, whereas the successful field rows were captured at
`0x006AB400`. The next bounded experiment is one same-run oracle capture that
keeps the positive control and hangar phase, adds the second 512-wide origin,
and enables an any-phase field dump for the empty path.

Competing hypotheses:

- `H-Retail94648-OriginMismatch`: field rows exist at `0x80094648`, but the
  prior exact-origin phase gate excluded them. Rows with width 512 and origin
  `0x006AB800` select this.
- `H-Retail94648-PreTargetOnly`: the PC executes only outside the target
  phase. Any-phase rows with no 512-wide target origin select this.
- `H-Retail94648-FieldUnsupported`: the execution watch fires in a target
  phase but the field dumper cannot read this PC's expected fields. Target
  execution with zero any-phase field rows selects this.

Discriminator: the `pc-field-dump` summary and row origins for
`0x80094648`, with the whole-RDRAM control and target VI as positive controls.
Do not alter runtime, selector, clear, task, audio-route, or payload state.

Exact command:

`OUT=scratch/agent/oracle_s3722_retail_94648_fields; mkdir -p "$OUT"; tools/oracle/build/rs64_oracle --core "$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" --rom "$HOME/Documents/Tools/rogue_squadron64/rogue_squadron.z64" --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 70 --hit-cap 64 --watch-write 0x0:0x800000 --watch-pc 0x80033FCC,0x80029E80,0x80029F30,0x80094648 --pc-phase-log-width 0x006AB400:512 --pc-phase-log-width 0x006AB800:512 --pc-field-dump 0x80033FCC --pc-field-dump 0x80029E80 --pc-field-dump 0x80029F30 --pc-field-dump-any-phase 0x80094648 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > "$OUT/oracle.log" 2>&1; rc=$?; printf 'rc=%s\n' "$rc" > "$OUT/result.txt"; exit "$rc"`
