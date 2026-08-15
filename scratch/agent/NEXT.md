# NEXT work unit (s1231)

HYPOTHESIS-ID: eeprom-state-entry

The s1230 save-media audit selected H1 for a real, selected, nonblank EEPROM.
Run one phase-gated paired retail oracle comparison: the existing EEPROM path
versus a separate temporary `SaveSRAMPath` containing a formatted blank
512-byte EEPROM. Do not alter the existing save file. Preserve whole-RDRAM and
PIF/VI positive controls in both arms.

Competing hypotheses and discriminator:

- H1: existing persistent state is required for the later retail path; only
  the existing-file arm leaves VI 320/origin `0x006dd280` and the blank arm
  reaches a different phase.
- H2: persistent state is irrelevant; both arms have the same phase-gated VI
  outcome.
- H3: blank formatting or path selection is invalid, shown by a failed
  whole-RDRAM/PIF/VI positive control or an unexpected EEPROM size/path.

Discriminator: compare the first post-boot VI transition and final VI
origin/width between the two arms, while requiring all controls to pass. A
phase difference selects H1; identical phase-gated outcomes select H2; failed
controls or wrong temporary file sizing selects H3.

Exact commands:

```
sed -n '1,240p' tools/oracle/README.md
rg -n -C 3 'SaveSRAMPath|format_eeprom|--press|VI|PIF' tools/oracle
mkdir -p /tmp/rs64-eep-blank
dd if=/dev/zero of=/tmp/rs64-eep-blank/blank.eep bs=512 count=1
# Run the repository's paired, phase-gated oracle recipe with the normal
# save path and with SaveSRAMPath=/tmp/rs64-eep-blank; use SIGKILL cleanup.
```
