# Next work unit: fold s5044 poison on/off (no census) verdicts
HYPOTHESIS-ID: m3-idiom-class-audit
s5043 (GUARD2 restored, census on) still stalled nohangar in both arms; only delta vs working s5037 is ROGUESQ_FREE_CENSUS=1. Queued s5044_poison_{off,on}_nocensus.sh.
Outcomes: both reach 0x6AB400+mission_onset and on-arm shows `[s5042-poison] total`  => compare crashes/verify_bad/divergence on vs off: differences => H-raf (read-after-free) supported; none => refuted on this route.
off arm stalls too => census was not the cause; route is flaky at this build -> run s5037_copy_guard_default again as control before more arms.
on arm reaches but no poison total => hook not firing (instrument invalid, null worthless).
Then: caller attribution (guest ra) of rs_free ptrs with header size 0x10 (0x80787810, 0x8075A010).
