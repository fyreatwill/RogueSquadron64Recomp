# NEXT work unit — M3 voice-array base publication census

HYPOTHESIS-ID: m3-voice-array-base-publication

## Single work unit

M5 target-phase qualification remains blocked: do not repeat the `s2618`
or eleven-Start routes. M4 hangar dest identity is closed (s3218:
`gspTask` `0x0075C000`/`0x00781800`, not `0x4B7800`). Next eligible unit
is a systematic M3 idiom-class audit of every generated publication of
the voice-array base (M5 plan A9), matching the s3216 list-head census.

Competing hypotheses:

- `H-NamedProducersOnly`: every store of the voice-array base is in the
  named allocate/reset family, and loads are range-checked or null-safe.
- `H-InvalidPublisher`: at least one generated store writes a non-KSEG0
  or overlapping base that the existing guard is papering over.
- `H-NoLiveBase`: the generated tree has no remaining base publication
  beyond already-named sites; the guard stays safety-only.

Discriminator: a complete grep census of base-pointer stores/loads with
companion names, caller fan-in, and whether any publisher is out of
range at generated-source scope. No port run. No new guard without a
named illegitimate writer.

Exact start: grep the generated snapshot and `funcs_24.c` / A9 sites for
the voice-array base symbol and `0x8015xxxx` stores; classify every hit
in one table.
