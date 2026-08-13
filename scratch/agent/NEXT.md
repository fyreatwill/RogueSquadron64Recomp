# NEXT work unit (audit the repeat drawIndexedTri G_CYC_COPY crash idiom)

HYPOTHESIS-ID: m3-drawindexed-copy-cycle

Perform one bounded source-only idiom audit of every `drawIndexedTri` assertion
or `G_CYC_COPY` guard and every caller/state setter that can reach it. Do not
change behavior or add a mitigation. Establish whether the abort is caused by
a legitimate copy-cycle triangle, stale cycle state, or a wrong opcode/handler
path, and identify the exact writer/transition before any runtime retry.

Competing hypotheses and discriminator:

- H-copy-cycle-legitimate: a real copy-cycle TRI reaches `drawIndexedTri` and
  the assertion reflects an unsupported but legitimate state.
- H-cycle-state-stale: an earlier state writer leaves `G_CYC_COPY` active when
  a normal triangle reaches the renderer.
- H-wrong-handler: a malformed or misdecoded command routes to the triangle
  helper with an invalid cycle mode.

Discriminator: exhaustive source paths and state writes classify the reachable
cycle-mode transition and caller; an explicit legitimate copy-cycle TRI selects
H-copy-cycle-legitimate, a stale prior writer selects H-cycle-state-stale, and
a wrong/malformed dispatch path selects H-wrong-handler. A runtime retry is
not justified until this audit identifies the relevant transition.

Exact execution: run bounded `rg` inventories over `lib/rt64/src` for
`drawIndexedTri`, `G_CYC_COPY`, `cycleType`, and all triangle callers; read each
hit in bounded windows and trace every setter-to-caller path. Record the
writer, value, and legitimacy classification for each path. No build or run is
needed unless the source audit leaves mutually exclusive live paths.
