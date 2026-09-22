# Next work unit: qualify retail parity for callback ownership

HYPOTHESIS-ID: m5-ai-post-pcm-consumer-ownership

Session 3719 selected a distinct port callback ownership boundary: image-stage
and PCM-consumer rows had different explicit sources and stable host-thread
identities, including 96 shared route ordinals. Retail parity is still open
because the debugger-enabled oracle core was unavailable.

Competing hypotheses:

- `H-RetailCallbackParity`: retail exposes the same distinct image-stage and
  PCM-consumer callback ownership, strengthening the cross-implementation
  boundary.
- `H-RetailSharedCallbackState`: retail uses one callback source/thread, so
  the port's split is a host-bridge divergence and the queue explanation must
  be reopened.
- `H-RetailOracleUnavailable`: the required debugger-enabled core is absent;
  no retail conclusion is allowed and the blocker must be recorded.

Discriminator: verify the oracle debugger-enabled core before building. If it
exists, run the retail oracle with the target-phase callback/source/thread and
route join, after arming its independent whole-RDRAM positive control. A
matching split selects `H-RetailCallbackParity`; a shared retail path selects
`H-RetailSharedCallbackState`; absent core selects `H-RetailOracleUnavailable`.
Do not change selector, clear, task, audio route, or payload state.

Commands:

`rg -n "debugger|core|mupen|oracle" tools/oracle README.md docs | head -80`

`sed -n '1,220p' tools/oracle/README.md`

`make -C tools/oracle`

`tools/oracle/<existing-retail-recipe-with-positive-control>`
