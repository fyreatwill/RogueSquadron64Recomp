# NEXT work unit (s2279) — complete the retail key-on pointer/state join

HYPOTHESIS-ID: m5-keyon-pointer-branch-discriminator

## Work unit

Add one oracle-side execution-field dump, then run one qualified port/retail
comparison using the already-built port witness. At each of the eight
post-guard transfer PCs, the oracle must print the live `$s0`/`$s1` pointers
and the guest words read at `$s0+0x60`, `$s0+0x22`, and `$s1+0x22`. Keep the
dump phase-gated to `width=512, origin=0x006AB400`; do not change the port
runtime, key-on return, divide guards, slot stores, audio default, or route
gates. This is one complete table, not another individual diagnostic field.

s2278 result to carry forward: the qualified port fired one new row at each
of the eight sites with `raw_ptr=0x801772F0`, `source_word=0x00C0053F`,
`branch_selector=0`, and `branch_state=0x6F5F`. Retail independently passed
the whole-RDRAM control, title/hangar gates, and all eight transfer PCs; its
matching caller rows showed denominator `$a0=0xC0` and selector `$v0=0`, but
retail pointer addresses varied within the voice list. Therefore the current
pointer/data-side lead is not yet a complete verdict until the retail pointed
words and destination state are joined at the transfer site.

## Competing hypotheses and discriminating measurement

- **H-PointerData:** retail and port selector/state words agree, while the
  pointed source word or normalized pointer/data identity differs. This
  selects a pointer/data contract boundary.
- **H-BranchState:** the source word and normalized pointer/data agree, while
  selector or destination state differs. This selects a branch-state
  publisher/predicate boundary.
- **H-Mixed:** both source/pointer and branch fields differ in the same
  qualified cells. Split the two inputs with a follow-up capture; no behavior
  change is authorized.
- **H-CoverageInvalid:** the oracle whole-RDRAM control, both retail phase
  gates, the port title/hangar controls, or any of the eight field buckets is
  absent/overflowed. The comparison is unevaluable.

The one discriminating table is keyed by
`phase,origin,width,transfer_pc,normalized_tuple` and has
`port_or_retail,raw_pointer,source_word,branch_selector,branch_state,count,
overflow,whole_rdram_control,title_gate,hangar_gate`. Absolute heap pointers
must not be treated as identity until the pointed words and their offset from
the voice-list base are compared.

## Exact commands

First add the single oracle option `--pc-field-dump A[,B...]` in
`tools/oracle/rs64_oracle.c`: for matching execution PCs, print `$s0`, `$s1`,
`MEM_W($s0+0x60)`, `MEM_BU($s0+0x22)`, and `MEM_HU($s1+0x22)` whenever the
existing `--pc-phase-log-width 0x006AB400:512` gate matches. Update the usage
line and rebuild the oracle:

```sh
tools/oracle/build.sh
```

Then launch both arms from the repo root in one shell, with the existing
qualified eleven-Start route for the port and the independent retail
whole-RDRAM control. Use the eight transfer PCs
`0x80090CF0,0x80090D08,0x80090D34,0x80090D4C,0x80090D78,0x80090D90,
0x80090DBC,0x80090DD4` for the field dump and the existing port witness:

```sh
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_RUNNER=1 ROGUESQ_LOG_RUNNER_ALL=1 ROGUESQ_LOG_THREAD_RESUME=1 ROGUESQ_LOG_OST_WB=1 PROBES_OVERRIDE='p1:start:5 p2:start:3' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2279_m5_keyon_pointer_branch_join 20 12 > scratch/agent/s2279_m5_keyon_pointer_branch_join_driver.log 2>&1 &
PORT_PID=$!
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 70 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 --watch-write 0x0:0x800000 --watch-pc 0x80090CF0,0x80090D08,0x80090D34,0x80090D4C,0x80090D78,0x80090D90,0x80090DBC,0x80090DD4 --pc-field-dump 0x80090CF0,0x80090D08,0x80090D34,0x80090D4C,0x80090D78,0x80090D90,0x80090DBC,0x80090DD4 --pc-phase-log-width 0x006AB400:512 --vi-trace > scratch/agent/s2279_retail_keyon_pointer_branch_join 2>&1 &
RETAIL_PID=$!
wait "$PORT_PID"; PORT_RC=$?
wait "$RETAIL_PID"; RETAIL_RC=$?
printf 'port_rc=%s retail_rc=%s\n' "$PORT_RC" "$RETAIL_RC"
```

Accept the comparison only if the whole-RDRAM watch reaches 10,000 writes,
retail reaches title and hangar, the port reaches title and
`512 @ 0x006AB400`, all eight port rows and all eight retail field buckets
fire, and no bucket overflows. Record the selected hypothesis and keep any
remaining field-join limitation explicitly single-source.
