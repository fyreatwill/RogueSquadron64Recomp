# NEXT work unit (s1213)

HYPOTHESIS-ID: retail-entry-strategy

Work unit: perform one bounded source/configuration audit of the available
mupen64plus front-end/core setup for an external savestate, reset-state, or
direct controller-state injection route that can preserve debugger callbacks
and the existing whole-RDRAM/PIF/VI positive controls. Do not run the game or
add instrumentation.

Competing hypotheses and discriminator:

- H1: the installed front-end/core exposes a usable alternate route; use it
  for the next debugger-enabled driven/undriven reachability comparison.
- H2: no usable external route is available; the retail investigation remains
  blocked on obtaining one.
- H3: a route exists but cannot preserve the positive-control setup; validate
  that incompatibility before using the comparison.

Discriminator: a concrete installed executable/API/config path, its invocation
point, and whether it leaves the existing whole-RDRAM/PIF/VI controls intact.
Documentation or a grep hit without a callable path is H2.

Exact commands (run from the repository root; inspect only, no game run):

    rg -n -i 'savestate|save state|load state|reset|direct.*pad|pad.*direct|controller.*inject|inject.*controller|SDL.*button|press' tools/oracle /opt/homebrew/include /opt/homebrew/share/mupen64plus 2>/dev/null
    rg -n -i 'm64p_command|SAVE|LOAD|STATE|RESET|SEND_SDL|BUTTON|input' /opt/homebrew/include /opt/homebrew/share/mupen64plus 2>/dev/null
    command -v mupen64plus || true
    ls -l /opt/homebrew/bin/mupen64plus /opt/homebrew/lib/mupen64plus 2>/dev/null || true

If H1 is selected, document the exact callable route and design one paired
60-second oracle run. If H2 is selected, ask for or install no plugin in this
iteration; record the specific missing capability and identify the narrowest
human/environment change needed. If H3 is selected, repair the
control-preserving invocation before running the comparison.
