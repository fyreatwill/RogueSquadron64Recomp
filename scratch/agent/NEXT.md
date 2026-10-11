# NEXT: identify the bad operands that produce FE98's derived cart value
HYPOTHESIS-ID: m5-audio-destub
Completed this iteration: the retail oracle reached VI origin `0x006AB400` at width 512 and wrote B0xxxxxx pointers at the target; the corrected three-arm port watch reached the same phase, passed `[s4569-control]` in all arms, and `[s4532-fill]` showed `site=FE98 dev=0x6C637265 size=0x300` in all arms. The static census then showed FE98 copies node `+8`, which `fillSampleStreamRange` computes as `a1 - node+4`; all four callers derive `a1` from voice `+0x34` plus calculated offsets. No ROM/resource lookup or tag translation exists on this chain. H-resource-key is refuted; H-derived-field-corruption remains the lead, with H-caller-input still possible.

Run next, in order:

1. Use the qualified retail route first (`zsh scratch/agent/s4591_oracle_tag.sh`) as the independent operand/role ground truth; do not build the port instrument until the retail target again reaches VI origin `0x006AB400` at width 512.
2. Batch one port build/instrument at `0x8008FDC0` and one qualified run. Record, phase-scoped, node address, node+4, caller a1/a2/a3, computed node+8, node+0/+C/+10/+14, and the cache-list identity. Keep the existing adjacent-range positive control and require the VI-512 gate.
3. Interpret the same-run rows: wrong node+4 with a sane caller source selects stale cache/node state; wrong a1/a3 selects caller/input; an external writer/translation is required before claiming a port-only producer. Do not add a mitigation.

Discriminator: the first bad operand at the `0x8008FDC0` subtraction, with a same-run positive control, splits stale cache state from caller/input. Ground truth is the retail capture, not the port runtime.
