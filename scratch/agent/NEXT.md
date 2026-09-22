# Next work unit: classify retail target guest paths

HYPOTHESIS-ID: m5-ai-post-pcm-consumer-ownership

Session 3720 established independent retail target-phase guest execution at
four watched PCs, but host callback/thread ownership is not observable in the
oracle. The next bounded experiment is one same-run retail field table at the
four active paths, with the whole-RDRAM and hangar controls retained.

Competing hypotheses:

- `H-RetailImageAndAudioFieldsDistinct`: target-phase field values at the
  watched paths form distinct task/audio roles, supporting the port's split.
- `H-RetailGuestPathsAliasState`: the distinct PCs consume the same state
  object/fields, so guest-path multiplicity does not support callback ownership.
- `H-RetailFieldTableUnevaluable`: the PCs fire but the debugger field table
  cannot capture the target phase; no role conclusion is allowed.

Discriminator: `--pc-field-dump` rows at all four PCs, phase-gated to
`0x006AB400:512`. Distinct stable field tuples across the paths select the
first hypothesis; shared tuples select the second; zero target rows with a
positive control and hangar VI select the third.

Exact command:

`OUT=scratch/agent/oracle_s3721_retail_guest_fields; mkdir -p "$OUT"; tools/oracle/build/rs64_oracle --core "$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" --rom "$HOME/Documents/Tools/rogue_squadron64/rogue_squadron.z64" --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 70 --hit-cap 64 --watch-write 0x0:0x800000 --watch-pc 0x80033FCC,0x80029E80,0x80029F30,0x80094648 --pc-phase-log-width 0x006AB400:512 --pc-field-dump 0x80033FCC --pc-field-dump 0x80029E80 --pc-field-dump 0x80029F30 --pc-field-dump 0x80094648 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > "$OUT/oracle.log" 2>&1; printf 'rc=%s\n' "$?" > "$OUT/result.txt"`

Do not change runtime code or audio/selector/payload state before this capture.
