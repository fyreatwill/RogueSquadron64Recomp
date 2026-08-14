# NEXT work unit (s953)

Pre-run decision: source-only caller audit; do not build, run the game, land a
guard/mitigation, or enqueue a soak until guest `$sp` provenance is classified.

HYPOTHESIS-ID: m3-slotdispatcheriter-stacksp-class

`slotDispatcherIter+872` is the recurring terminal SIGBUS, but s952 mapped it
to `funcs_8.c:22810`: the prologue spill `MEM_W(0x1C, ctx->r29)`. The callee
fails while saving registers, before it reads `gNpcSlotList`; the active class
is caller-supplied guest stack-pointer state. The source has 144 direct call
sites in 19 generated files. Follow the `-0x25A4` idiom-class model and
enumerate every caller's frame setup, call boundary, and epilogue.

Step 1: enumerate the 144 direct sites and their enclosing functions. For each
site, record nearby `ctx->r29` adjustments and any calls that can return with
the context changed. Cross-check guest addresses against `funcs.h` and
`../rogue_squadron64/symbol_files/main_overlay.txt`.

Competing hypotheses:

- H-slotdispatcheriter-stacksp-caller-corruption: a caller enters with a wild
  or mis-restored `$sp`, selecting a real caller-side corruption class.
- H-slotdispatcheriter-stacksp-balanced: all callers are structurally
  balanced; the invalid `$sp` is introduced by shared runtime/context state.
- H-slotdispatcheriter-stacksp-stub-artifact: a known degenerate stub path
  corrupts the shared context before a normal caller invokes the dispatcher.
- H-slotdispatcheriter-stacksp-unclassified: the caller/writer set is not yet
  fully enumerated.

Discriminating measurement: complete caller-site inventory of `$sp` prologue,
epilogue, and call-boundary state, cross-checked with companion symbols. An
unbalanced or wild caller selects caller corruption; balanced callers with no
shared-state writer select runtime/context state; a chain rooted in a known
stub selects stub-artifact; anything unresolved selects unclassified.

Exact starting commands:

`rg -n "slotDispatcherIter\\(rdram, ctx\\);" ../N64Recomp/RecompiledFuncs/funcs_*.c`

`rg -n -B12 -A8 "slotDispatcherIter\\(rdram, ctx\\);" ../N64Recomp/RecompiledFuncs/funcs_*.c`

`rg -n "ctx->r29 =|MEM_W\\(.*ctx->r29|addiu.*\\$sp|jal.*8003E8DC" ../N64Recomp/RecompiledFuncs/funcs_*.c`

Cross-check the resulting guest addresses against
`../rogue_squadron64/symbol_files/main_overlay.txt` and `funcs.h`.
