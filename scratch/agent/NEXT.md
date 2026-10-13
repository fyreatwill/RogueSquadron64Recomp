# RESUME — next work unit: census every shutdownAudioEngine caller

HYPOTHESIS-ID: m5-callback-teardown-duplicate-slot

The s4771 qualified route reaches title and hangar, confirms first-match
deregistration leaves a duplicate callback live, and never enters
`shutdownAudioEngine`. Before another runtime instrument, perform one bounded
static caller census to identify whether shutdown has an alternate reachable
caller or is only a shutdown-state path.

Competing hypotheses and discriminating measurement:

- H-shutdown-alt-caller: a generated direct caller or address-taken dispatch
  can reach `shutdownAudioEngine` on a route not covered by the autopilot.
- H-shutdown-only-init: all callers are initialization/shutdown-state paths;
  the title/hangar route cannot reach this function without a distinct state
  transition.
- H-symbol-alias: the apparent shutdown function is aliased or wrapped, so a
  name-only census misses the live call target.

DISCRIMINATING MEASUREMENT: enumerate every direct call and every function
pointer/address reference to guest PC `0x80091D40`, independently compare the
generated tree with the companion decomp symbol/call graph, and classify each
caller by its surrounding state gate. A direct target-phase caller selects
H-shutdown-alt-caller and names the next phase-gated route; only init/shutdown
state callers plus no address-taken alias selects H-shutdown-only-init and
parks this teardown branch. Any address-taken or wrapper reference selects
H-symbol-alias and requires a single target-PC witness before a new soak.

Commands:

```sh
rg -n "80091D40|shutdownAudioEngine\(" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64
rg -n "shutdownAudioEngine|80091D40" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | sort
```

Do not build or change deregistration behavior in that census. If it selects a
new caller, the following unit must batch a target-PC positive-control oracle
watch and the corresponding port phase witness in one build/run.
