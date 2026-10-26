# Next: rerun the terrain-radius probe on valid wide flight
HYPOTHESIS-ID: g3c-owner-visual

s6294 added the fixup-backed `ROGUESQ_G3C_EDGE_WRITER` probe at guest PC
0x80043918 and built it successfully. Retail level 1 held 204 s clean with
the positive control firing. The first wide recipe used the wrong title-origin
gate; the corrected retry reached the 1024-wide origin but ended
`nomission-att1`. Do not interpret its pre-flight samples as a terrain result.

One bounded work unit: rerun retail and 21:9 concurrently with the same binary,
using the origin-agnostic phase gates below. Competing hypotheses remain
H-aspect (radius unchanged, widened frustum exposes edge), H-radius (raw or
effective radius changes), H-fade (radius unchanged but projection/fog writer
changes), and H-retail (retail flight shows the same edge). The discriminator
is the probe's `raw/eff/valid` rows after mission phase plus the existing edge
score/contact sheet. Missing mission or missing probe is VOID, not a null.

    env ROGUESQ_G3C_EDGE_WRITER=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' ROGUESQ_G1B=1 XENV_EXTRA='ROGUESQ_G3C_EDGE_WRITER=1' HOLD_S=200 LEVEL=1 TAG_SUFFIX=s6295_retail zsh scratch/agent/g1_level_coverage_common.zsh
    env ROGUESQ_G3C_EDGE_WRITER=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' ROGUESQ_G1B=1 XENV_EXTRA='ROGUESQ_G3C_EDGE_WRITER=1 ROGUESQ_ASPECT=21:9 ROGUESQ_OSMEM_MB=12' HOLD_S=200 LEVEL=1 TAG_SUFFIX=s6295_wide zsh scratch/agent/g1_level_coverage_common.zsh

Do not add a fog/radius mitigation. If both arms reach flight and radius is
unchanged, static-enumerate the projection/fog writer next; otherwise fix only
the harness gate and rerun this same probe.
