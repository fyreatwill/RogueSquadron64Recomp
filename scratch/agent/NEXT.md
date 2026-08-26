# NEXT work unit (s2380) — M5 A1 effective retail receive flag

HYPOTHESIS-ID: m5-a1-retail-flag-semantics

## Work unit

Resolve the effective `$a2` received by retail `osRecvMesg` at the
`0x80001CB8` call without changing the port. Use one independent source that
can observe the callee-entry argument or decode the retail instruction at the
delay-slot address. First verify the address mapping against the known port
instruction sequence; do not infer the effective flag from the pre-delay
call-site register.

## Competing hypotheses and discriminating measurement

- H-RetailNonblocking: retail supplies zero to the callee and uses
  nonblocking semantics.
- H-RetailBlockingObserved: retail's delay slot or ABI path supplies a
  nonzero/blocking flag.
- H-RetailLabelArtifact: the proposed source/measurement does not identify the
  same call ordinal.

The discriminator is a single joined row keyed by the retail call ordinal:
callee-entry `$a0/$a1/$a2`, the preceding `0x80001CB8` call, and return to
`0x80001CC0`. Zero at callee entry selects H-RetailNonblocking; nonzero
blocking semantics selects H-RetailBlockingObserved; failure to join the
callee and successor selects H-RetailLabelArtifact. A decoded delay-slot
instruction may select the first two only if its ROM-to-RAM address mapping is
independently verified.

## Exact commands / controls

Read `tools/oracle/README.md` before changing the oracle recipe. If extending
the oracle, keep `--watch-write 0x0:0x800000`, the two target 640 origins, and
the `0x80001CB8`/`0x80001CC0` watches in the same run. The s2379 baseline was:

    env tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 42 --hit-cap 120 --watch-write 0x0:0x800000 --watch-pc 0x80001CB8,0x80001CBC,0x80001CC0 --pc-phase-log-width 0x00696100:640 --pc-phase-log-width 0x00696600:640 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start

Expected outcomes: the delay-slot watch may remain zero because the debugger
does not breakpoint MIPS delay slots; that is a measurement limitation, not
evidence for either flag hypothesis. Do not change the port flag, fallback,
dispatch, VI, task, or audio behavior.
