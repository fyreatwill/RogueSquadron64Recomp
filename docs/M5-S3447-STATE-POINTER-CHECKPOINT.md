# M5 session 3447 — state-pointer checkpoint result

The retail oracle ran for 70 seconds with a whole-RDRAM positive control, both
hangar 512 origins, and execution watches at `0x80001C98`, `0x80001CB8`,
`0x80001CC8`, and `0x80001F84`. All controls fired; retail's dominant
`rs_free` predecessor was `0x80005268`.

One build added ordered port witnesses immediately after `osRecvMesg_recomp`
and immediately before the existing consumer witness. A concurrent first run
crashed before the phase gate in the pre-probe scheduler path and was
discarded. The fixed sequential silent/image run reached title 1024 and
hangar 512 in both arms without crash or abort.

| arm | entry | post-receive | pre-consumer | consumer |
|---|---:|---:|---:|---:|
| silent | 401 | 401 | 401 | 512 |
| image | 408 | 408 | 408 | 512 |

The ordered 512 rows retained `s1=0x80194B20`, pointed word
`0x80194B40`, and state `0x801BEEB0` in both arms. Existing consumer rows
were title-1024 calls using `0x801BBD..` state pointers, so the new
checkpoints did not join to those consumer rows. This is positive
instrumentation but unevaluable for the title-1024 clobber boundary; it
neither proves parity nor identifies a writer there.

Artifacts: `scratch/agent/s3446_m5_state_pointer_clobber/oracle/` and
`scratch/agent/s3446_m5_state_pointer_clobber/port/`.
