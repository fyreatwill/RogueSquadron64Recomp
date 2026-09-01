# NEXT work unit — resolve the higher-level source destination contract

HYPOTHESIS-ID: m5-preclear-destination-contract

Session 3544 selected `H-PortPrephaseCPU`: the process-lifetime port census
observed 268 hangar-span CPU stores in width-640 phase, 104 nonzero, followed
by hangar `rs_memset` entry with `pre_nz=155`. Do not repeat that census.

Do exactly one bounded work unit: instrument the already identified retail
texture-record store family (`0x8001FACC`–`0x8001FD2C`) to capture its base/
index context and destination relation, then run the same watch in the retail
oracle and the same-build real-audio port. Keep all audio, PCM, image-task,
and output state unchanged.

Competing hypotheses and discriminator:

- `H-SharedDestinationContract`: retail and port execute the family with the
  same destination relation and payload class; the remaining gap is upstream
  source selection.
- `H-PortWrongDestination`: the port's base/index selects the hangar source
  span while retail selects a distinct texture-record destination; differing
  context precedes the stores.
- `H-RetailOnlyFamily`: retail executes this family in the target phase but the
  port does not; the observed port rows belong to a different route/use.
- `H-CaptureInvalid`: whole-RDRAM and both phase controls or the paired family
  witnesses are absent.

The single discriminating table must include, for each family store, phase/VI,
PC, base register, effective destination, payload, and the nearest source
selection/caller context. Matching context selects `H-SharedDestinationContract`;
a first differing base/index selects `H-PortWrongDestination`; a retail-only
execution selects `H-RetailOnlyFamily`; missing controls select
`H-CaptureInvalid`.

Before building, retain `scratch/agent/retail_preclear_groundtruth.log` and
read the existing family injection in `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
Batch the instrumentation, then build and run both oracle and port arms in one
iteration. Use VI phase gates, SIGKILL cleanup, and capture under:

    scratch/agent/s3545_m5_destination_contract
