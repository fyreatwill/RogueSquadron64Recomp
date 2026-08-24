# NEXT work unit (s2280) — complete the retail key-on pointer/state join

HYPOTHESIS-ID: m5-keyon-pointer-branch-discriminator

## Work unit

Raise the oracle's per-PC unique-field capacity from 256 to 32768, rebuild the
oracle, and run one pair with the established eleven-Start route driver. The
existing `--pc-field-dump` must remain phase-gated to
`width=512, origin=0x006AB400`; do not change the port runtime, key-on return,
divide guards, slot stores, audio default, or route gates. This is a capacity
fix for the measured saturation, not a new field or a behavior arm.

s2279 result to carry forward: the oracle field dump fired at all eight PCs and
retail passed the whole-RDRAM, title, and hangar controls, but every 256-row
bucket saturated (`hits=17,987`, overflow `14,718`–`15,911`) while the fixed
port route stopped at off-target `512 @ 0x00690400`. s2278's qualified port
row remains `raw_ptr=0x801772F0`, `source_word=0x00C0053F`, selector `0`, and
state `0x6F5F`; the next capture must first qualify the port hangar before any
retail field comparison is interpreted.

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
  gates, the port title/hangar controls, any of the eight field buckets, or
  the no-overflow condition is absent. The comparison is unevaluable.

The one discriminating table is keyed by
`phase,origin,width,transfer_pc,normalized_tuple` and has
`port_or_retail,raw_pointer,source_word,source_byte,branch_selector,branch_state,count,overflow,whole_rdram_control,title_gate,hangar_gate`.
Absolute heap pointers must not be treated as identity until the pointed words
and their offset from the voice-list base are compared.

## Exact commands

First change `MAX_PC_FIELD_DUMP_ROWS` from `256` to `32768` in
`tools/oracle/rs64_oracle.c` and rebuild the oracle:

```sh
tools/oracle/build.sh
```

Then launch both arms from the repo root using the established route driver;
it already supplies the eight transfer PCs, the oracle positive control, the
hangar phase gate, and the port witness:

```sh
zsh scratch/agent/run_s2278_m5_keyon_pointer_branch.sh s2280_m5_keyon_pointer_branch_capacity
```

Accept the comparison only if the whole-RDRAM watch reaches 10,000 writes,
retail reaches title and hangar, the port reaches title and
`512 @ 0x006AB400`, all eight port rows and all eight retail field buckets
fire, and no bucket overflows. If any route gate or bucket fails, select
H-CoverageInvalid and do not infer H-PointerData, H-BranchState, or H-Mixed.
If qualified, compare normalized pointer/data identity against selector/state;
keep any remaining field-join limitation explicitly single-source.
