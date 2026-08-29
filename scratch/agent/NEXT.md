# NEXT work unit — M3 musyxKeyOnVoice divisor/descriptor census

HYPOTHESIS-ID: m3-keyon-divisor-descriptor

## Single work unit

M5 target-phase qualification remains blocked: do not repeat the `s2618`
or eleven-Start routes. A9 voice-array base publication is closed (s3219:
sole store `0x8008F0EC` in `allocateSongChannelArray`). Next eligible unit
is the A8 idiom-class audit of every divisor/descriptor writer for the
eight `musyxKeyOnVoice` trap sites.

Competing hypotheses:

- `H-NamedDescriptor`: every divisor loaded at the eight trap PCs is
  written by a named voice/channel descriptor path with a finite range.
- `H-InvalidDivisorProducer`: at least one generated store writes a zero,
  overflow, or non-voice value into a divisor field the traps are papering
  over.
- `H-NoLiveDivisorWriter`: the generated tree has no remaining store into
  those fields beyond already-named sites; the traps stay safety-only.

Discriminator: a complete grep census of the eight trap sites' divisor
loads, the backing record fields, every generated store into those
fields, companion names, and caller fan-in. Classify each writer as
in-range, out-of-range at source scope, or unresolved. No port run. No
trap removal without a named legitimate writer.

Exact start: grep `funcs_24.c` `musyxKeyOnVoice` at `0x80090A3C` for the
eight PCs `0x80090CEC`, `0x80090D04`, `0x80090D30`, `0x80090D48`,
`0x80090D74`, `0x80090D8C`, `0x80090DB8`, `0x80090DD0`; recover the
loaded field offsets; census every store of those offsets in the
generated snapshot.
