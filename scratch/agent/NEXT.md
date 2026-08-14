# NEXT work unit (s1102)

HYPOTHESIS-ID: submit-producer-boundary

Perform one bounded static audit of every generated `osSendMesg` and
`osJamMesg` path that could target the separately initialized queues
`0x8011A818` and `0x8011A7E8`, plus the host forwarding code that can enqueue
SP/DP completion messages. Do not change queue behavior or build.

Competing hypotheses:

* H-game-producer: generated code sends to one or both blocking queues, so the
  event registrations are intentionally for separate completion queues.
* H-host-boundary: neither queue has a generated producer; one queue is meant
  to be populated only across a non-generated host/overlay boundary.
* H-unwired: neither queue has a producer or forwarding path, so the blocking
  waits are genuinely disconnected from the registered event queues.

Discriminator: produce a complete target table for all static send/jam sites
and host enqueue sites. A direct generated send to each queue selects
H-game-producer; a host-only route selects H-host-boundary; no route to a queue
selects H-unwired. Any unresolved computed target must name its exact
non-generated boundary rather than infer a match.

Exact commands:

```sh
rg -n -C 5 "osSendMesg|osJamMesg|0x8011A818|0x8011A7E8|D_8011A818|D_8011A7E8|0X8012.*57E8|0X8012.*5818" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs src lib/N64ModernRuntime docs/game-architecture.md
rg -n -C 5 "enqueue_external_message|enqueue_external_message_src|events_context\.sp|events_context\.dp|sp_complete|dp_complete" lib/N64ModernRuntime src
git diff --check
```
