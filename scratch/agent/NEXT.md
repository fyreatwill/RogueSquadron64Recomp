# NEXT work unit (s1101)

HYPOTHESIS-ID: submit-registration-source

Perform one bounded static source audit of the actual SP/DP event
registrations observed in s1100. Enumerate every generated call to
`osSetEventMesg`, resolve the queue-object initialization and aliases for
`0x8011A420` and `0x8011A408`, and reconcile them with the blocking consumers
at `0x8011A818` and `0x8011A7E8`. Do not change queue behavior or build unless
the audit requires a compile-time inspection.

Competing hypotheses:

* H-registration-source: generated registration calls intentionally bind SP
  and DP to `0x8011A420`/`0x8011A408`; the s1098 consumer addresses are stale or
  refer to different queue roles.
* H-queue-alias: one or both observed addresses are aliases of the blocking
  consumer objects after overlay/global relocation or pointer translation.
* H-real-mismatch: one or both observed registrations are distinct objects
  from the blocking consumers, leaving a genuine producer/consumer mismatch.

Discriminator: produce a complete table for each `osSetEventMesg` SP/DP call
with generated call site, event kind, queue expression, resolved guest
address, queue initializer, and all blocking consumer addresses. A direct
same-object resolution selects H-queue-alias; a distinct initialized object
selects H-real-mismatch; a complete source mapping showing the consumers are
different roles selects H-registration-source. If source cannot resolve a
case, name the exact non-generated boundary rather than inferring an alias.

Exact commands:

```sh
rg -n -C 4 "osSetEventMesg|D_8011A420|D_8011A408|0x8011A420|0x8011A408|0x8011A818|0x8011A7E8|OSMesgQueue" RecompiledFuncs src lib/N64ModernRuntime docs/game-architecture.md
rg -n -C 4 "osRecvMesg.*(8011A818|8011A7E8)|8011A818|8011A7E8" RecompiledFuncs src
git diff --check
```
