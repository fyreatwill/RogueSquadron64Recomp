# Next: join the remaining pre-selector source writers

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3669 passed whole-RDRAM, all four descriptor, title, hangar, and
type-2 task controls. The bounded exact-store arm showed that all 384 writes
from primary `0x800078EC` share one zero-fill context (`a0=0x801797B0`,
`a1=0`, `a2=0x298`, `ra=0x8008F2D4`). This is single-source evidence for
`H-PrimaryInitialization`; primary initialization is no longer the object
payload-owner candidate. The remaining 290 source-span writes are open.

Next unit: add bounded exact-store context rows for `0x80007670` and the
smaller source-span writer PCs identified by the existing writer histogram,
then compare each row's context with the next selector and task object. Keep
the whole-RDRAM positive control, all four descriptor watches, selector/task
watches, and title/hangar phase controls in the same run. Do not re-arm the
unbounded `--pc-field-dump 0x800078EC` arm.

Discriminator:

- H-RemainingObjectWriter: exact stores carry context that identifies the
  next selected object or a stable object-specific payload contract.
- H-RemainingInitialization: exact stores have invariant setup context like
  the primary zero-fill and do not distinguish selected objects.
- H-RemainingSeparateObjects: context transitions align with alternating
  `0x80171E70`/`0x80173CB0` hangar objects.
- H-CaptureInvalid: whole-RDRAM, title, or hangar control fails; discard the
  capture.

Before building, read `tools/oracle/README.md` and
`docs/F5-UCODE-REFERENCE.md`. Build once with `bash tools/oracle/build.sh`,
run one 55-second capture from `build/`, and store the log under
`scratch/agent/` with a non-dot final component. A mitigation or guest-state
rewrite is out of scope.
