# Session 2981 unblock measurement

Route 1 was tested with the existing M5 arms. The retail oracle control in
`s2981_unblock_step1_fixed/oracle.log` passed the whole-RDRAM threshold at
10,000 callbacks and observed title `1024 @ 0x00790400` followed by hangar
`512 @ 0x006ab400`. Its first wrapper did not launch arms because its phase
match expected the fields in the wrong order; that harness defect was fixed.

The repository's array-based arm driver then ran both controls concurrently
from `build/` with phase-gated probing. Silent (`ROGUESQ_AUDIO_UCODE=0`) and
image (`=1`) each dispatched 42 audio tasks. Silent reached only VI 320;
image reached VI 640 (`0x0066A500`). Neither reached title or hangar. Both
had zero crash and abort markers. The target-phase discriminator is therefore
unevaluable, and the route dependency remains real for this executable.
