# Next work unit: qualify the shared retail guest-field tuple

HYPOTHESIS-ID: m5-retail-shared-field-tuple

Session 3722 resolved the empty `0x80094648` table: the corrected oracle
capture produced 128 rows, all at target origin `0x006AB800`. The next
bounded experiment keeps both 512-wide origins and asks whether the shared
`0x80029E80`/`0x80029F30` tuple is intentional.

Competing hypotheses:

- `H-SharedTupleIntentional`: both PCs intentionally consume the same state
  object/fields. Repeated rows with the same `s0`, `s1`, source byte, and
  branch state at both origins select this.
- `H-SharedTuplePhaseAlias`: the tuple is shared only because the two PCs are
  sampled in a common phase/route bucket. Distinct tuples when origin and
  predecessor context are retained select this.
- `H-SharedTupleFieldArtifact`: the PCs do not share the relevant state, but
  the current field dumper reads a common or wrong location. Stable execution
  and origin rows with distinct register/pointer context but equal dumped
  fields select this.

Discriminator: one oracle run's full field-row table for both PCs at both
512-wide origins, retaining the 10,000-write whole-RDRAM control and all four
execution watches. A run that does not reach a 512-wide target is invalid.

Exact command:

`OUT=scratch/agent/oracle_s3723_retail_shared_tuple; mkdir -p "$OUT"; tools/oracle/build/rs64_oracle --core "$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" --rom "$HOME/Documents/Tools/rogue_squadron64/rogue_squadron.z64" --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 70 --hit-cap 64 --watch-write 0x0:0x800000 --watch-pc 0x80033FCC,0x80029E80,0x80029F30,0x80094648 --pc-phase-log-width 0x006AB400:512 --pc-phase-log-width 0x006AB800:512 --pc-field-dump 0x80033FCC,0x80029E80,0x80029F30,0x80094648 --pc-field-dump-any-phase --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > "$OUT/oracle.log" 2>&1; rc=$?; printf 'rc=%s\n' "$rc" > "$OUT/result.txt"; exit "$rc"`
