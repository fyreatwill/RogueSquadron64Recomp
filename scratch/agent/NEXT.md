# NEXT: is the "red VTX" detector just counting int16 sign bytes?
HYPOTHESIS-ID: g3c-owner-visual

s6349 showed no host write touches 0x735560..0x7355D0 before phase 7, and the logged "red" bytes
(FFA4 FEEF FFA4 0000 ...) are small negative int16 shorts with 0000 padding.

Hypotheses:
- H-false-positive: the detector (any of 3 byte lanes == 0xFF) flags 0xFF sign bytes of negative
  position shorts; there is no colour corruption.
- H-real-colour: the F5 vertex layout puts RGBA in these lanes, and they really are 0xFF.
- H-mixed: some ranges are pos-only (false positive), others have genuine colour lanes.

Discriminator (offline, no run): read docs/F5-UCODE-REFERENCE.md for the 0x04 VTX record layout
(stride, pos/colour offsets); decode the logged `registered=`/`read=` hex in
scratch/agent/m6/g1_lvl1s6349_host_target_write/run.log by field; count 0xFF per field.
Pos-only 0xFF => H-false-positive (retire the red-writer thread). Colour-field 0xFF => H-real-colour.
Then return to the actual G3c(a) jagged far-terrain edge measurement.
