# Next work unit (s4418): repair and qualify the port selector caller/precall witness

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4417's static census found the port caller/precall rows were absent
because the current generated `RecompiledFuncs/funcs_24.c` has no
`rs64_m5_selector_caller` or `rs64_m5_selector_precall` invocation or marker.
The live edge is `0x8009131C/0x8009132C -> 0x80091330`; the host callbacks and
standalone apply scripts exist, but the insertion is not retained in the
generated artifact.

Competing hypotheses:

- H-fixup-retains: the repaired regeneration-safe insertion appears at all
  three generated edge sites and fires with the existing controls.
- H-script-anchor-drift: the repair script cannot match the current generated
  form, so the marker remains absent after the prescribed generation step.
- H-divergence-before-selector: live caller/precall rows appear and differ from
  the retail predecessor tuple before selector entry.
- H-route-boundary: phase, selector, task, or image controls fail, so the
  comparison remains unevaluable.

Discriminating measurement: after repairing the regeneration-safe insertion,
the generated-file marker census and one qualified run must show the markers,
the caller/precall rows, and the existing positive controls in the same run.
Markers absent after regeneration selects H-script-anchor-drift; markers live
but rows absent with controls live selects a remaining route issue; live rows
selects the pre-selector divergence comparison.

Exact commands:

1. Repair the regeneration-safe insertion in the fixup/apply path, preserving
   the existing guest PCs and adding no new runtime fields.
2. Run the prescribed generation/fixup sequence, then verify with:
   `rg -n -C 4 'rs64_m5_selector_(caller|precall)|PATCH: s350[01]' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c`.
3. Build once and run the canonical qualified route with the existing M5
   selector/input, VI, task, image, and positive-control env vars. Kill with
   SIGKILL and compare marker, caller/precall, and control counts.
