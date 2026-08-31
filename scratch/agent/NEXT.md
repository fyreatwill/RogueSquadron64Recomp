# NEXT work unit — repair the frequency-contract join at osRecvMesg entry

HYPOTHESIS-ID: m5-frequency-writer-contract

Session 3436 showed that the planned port/retail tuple comparison was sampled
at different boundaries: retail `0x800331E0` is interior to `osRecvMesg`, but
the port witness is at `osRecvMesg_recomp` entry. The zero intersection is
therefore unevaluable, not evidence of a missing port tuple family.

Competing hypotheses and the single discriminating measurement:

- `H-PortTupleFamilyMatch`: entry-level retail and port tuple families share
  at least one exact tuple; the remaining gap is downstream of osRecvMesg.
- `H-PortTupleFamilyMissing`: the entry-level families have no exact match;
  the gap is earlier port input/dispatch behavior.
- `H-EntryJoinMissing`: the retail entry has no phase rows or the field set
  still cannot be joined; the boundary remains unevaluable.

Ground-truth command, changing the watched PC and field dump to the actual
function entry:

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 45 --hit-cap 200 --watch-write 0x0:0x800000 --watch-write 0x165ED0:0x165ED4 --watch-pc 0x800331D0 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x00790800:1024 --pc-field-dump 0x800331D0 --pc-hist-watch 1 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x00790800:1024 --post-value-watch 1 --post-value-pc 0x800331E0 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start --hold-ms 150 > scratch/agent/s3437_m5_frequency_entry/oracle.log 2>&1`

Then run one fresh-build port image arm with
`ROGUESQ_LOG_M5_FREQUENCY_CONTRACT=1` and the existing qualified phase
controls, capturing to `scratch/agent/s3437_m5_frequency_entry/run.log`.
Compare exact normalized `s0,s1,source_word,source_byte,branch_selector,
branch_state` sets. A matching tuple selects `H-PortTupleFamilyMatch`; no
match selects `H-PortTupleFamilyMissing`; no usable retail/port join selects
`H-EntryJoinMissing`. Keep waits, slots, dispatch, clear behavior, and PCM
writeback unchanged.
