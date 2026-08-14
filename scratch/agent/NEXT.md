# NEXT work unit (s1099)

HYPOTHESIS-ID: submit-external-queue-wiring

Perform one bounded static host/runtime audit of the two unmatched blocking
waits inside `submitGfxFrame`. Trace the external SP-completion producer for
`D_8011A818` and the DP forwarding producer for `D_8011A7E8` through
`src/main`, ultramodern events, and existing queue-control code. Do not build,
run, or change runtime code.

Competing hypotheses:

* H-host-wired: both external producers target the exact guest queues and use
  compatible message/event routes.
* H-sp-unwired: the SP completion route does not target `D_8011A818`.
* H-dp-unwired: the DP forwarding route does not target `D_8011A7E8`.
* H-address-mismatch: both routes exist but resolve to different queue objects.

Discriminator: produce a two-row table containing guest queue address, host
producer function, exact target address, event/message kind, and consumer. Two
exact producer targets select H-host-wired; a missing or wrong SP target selects
H-sp-unwired; a missing or wrong DP target selects H-dp-unwired; differing
queue-object identities select H-address-mismatch.

Exact commands:

```sh
rg -n "D_8011A818|D_8011A7E8|enqueue_external_message|sp_task_queue|dpInterrupt|OS_EVENT_DP|osSendMesg" src lib/N64ModernRuntime docs
sed -n 'START,ENDp' <host-or-runtime-file>
```
