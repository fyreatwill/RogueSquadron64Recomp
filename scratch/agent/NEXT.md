# Next work unit: independently classify alternate-family ownership

HYPOTHESIS-ID: m5-alternate-family-object-ownership

Session 3834 selected H3 at the port scope: 130 family-entry and 1,011
family-store rows exactly joined the authoritative audio-return route context,
all after that context, while source/consumer PCM matches stayed zero. This
does not distinguish intended route/service state from disconnected output.

Competing hypotheses and discriminator:

- H1: the alternate family is intended route/service state. An independent
  retail target-phase watch sees the same alternate-object writes or reads,
  with matching family PC and route ordinal/row evidence.
- H2: the family is disconnected output. Retail reaches the family PCs and
  target phases, but never touches the alternate object ranges corresponding to
  the port family stores.
- H3: the family is port-only post-return behavior. Retail has no qualified
  family/object parity, while the port retains the exact post-return joins and
  zero PCM matches.

The discriminator is one paired capture with a positive whole-RDRAM retail
watch, retail title/hangar VI gates, retail family-PC watches, and port
family-entry/store plus route-context controls. Reject it unless both arms
reach title 1024 and hangar 512 and all controls are positive. Classify only
from alternate-object address overlap and family-PC reachability; do not use
wall-clock order or infer ownership from the port route identity.

Before building, verify the oracle debugger preflight and read
`tools/oracle/README.md`; if the available core again lacks DEBUGGER=1 symbols,
record that setup failure and do not treat it as H2. Preserve the validated
port command from s3834, add only the independent retail watch arm, and use
SIGKILL cleanup. The evidence paths should be
`scratch/agent/s3835_m5_alternate_object_oracle/` and its oracle log.
