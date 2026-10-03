# Next work unit: M5 alternate-object legitimacy versus route identity

HYPOTHESIS-ID: m5-retail-writer-port-edge

Use s3770's boundary: in both port arms, S/L internal stores reached only
alternate object addresses in title and hangar; I produced title setup stores
but no hangar-phase store bucket. No family store reached either target
buffer. The next census must join those alternate objects to the clear
associated object and active route.

Competing hypotheses:

- H-M5-AlternateObjectLegitimate: S/L write a legitimate alternate asset
  object, and I is legitimately title-only setup.
- H-M5-RouteObjectIdentityMismatch: the family bodies derive an object that
  should be the clear-associated route object, but the port's route/object
  identity is mismatched.
- H-M5-I-HangarEdgeDropped: I's hangar absence is a call/phase edge loss,
  not legitimate setup-only behavior.

Discriminator: one regeneration-safe, phase-gated census that records each
S/L/I family store destination together with the clear-associated allocation
object from 0x8008F2CC, allocator return, route ordinal/row, and family
phase. H-M5-AlternateObjectLegitimate wins if alternate destinations match a
distinct, consistently allocated asset object and I remains setup-only.
H-M5-RouteObjectIdentityMismatch wins if they should match the clear/route
object but do not. H-M5-I-HangarEdgeDropped wins only if I's hangar call and
object are present in retail/port controls but its generated store edge is
missing.

Before building, locate the existing clear, allocator, route snapshot, and
s3770 store anchors with rg in funcs_2.c, funcs_6.c, funcs_23.c, and
fixup_game_funcs.py.

Use one fixup-script batch, one Debug build, and one concurrent oracle/image/
silent run. Keep the whole-RDRAM control, both target VIs, and all passive
breadcrumbs. Do not suppress or replace the clear, inject payloads, or change
an audio gate.
