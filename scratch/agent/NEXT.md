# NEXT work unit (s1212)

HYPOTHESIS-ID: retail-entry-strategy

Work unit: perform one bounded source audit of the oracle CLI and runner for an
unexposed savestate, reset-state, or direct pad-state injection route. Do not
run the game or add instrumentation.

Competing hypotheses and discriminator:

- H1: the source exposes a usable alternate route; use it for the next
  debugger-enabled driven/undriven reachability comparison.
- H2: only scheduled SDL button presses are exposed; the retail investigation
  remains blocked on finding another entry mechanism.
- H3: an apparent route exists but cannot preserve the positive-control setup;
  validate that route before using it.

Discriminator: source-level presence of a callable savestate/reset/direct-pad
route, together with its invocation point and whether it leaves the existing
whole-RDRAM/PIF/VI controls intact. A grep hit without a callable path is H2.

Exact commands (run from the repository root):

    rg -n -i 'savestate|save state|load state|reset|direct.*pad|pad.*direct|controller.*inject|inject.*controller|SDL.*button|press' tools/oracle
    rg -n 'argv|usage|m64p_core|Input.*State|BUTTON|sdl' tools/oracle --glob '*.[ch]' --glob '*.cpp'

If H1 is selected, document the exact callable route and design one paired
60-second oracle run. If H2 is selected, seek an external/front-end entry
strategy rather than repeating button timing. If H3 is selected, repair the
control-preserving invocation before running the comparison.
