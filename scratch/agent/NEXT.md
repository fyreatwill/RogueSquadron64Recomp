# NEXT work unit — resolve the texture-record base/index producer

HYPOTHESIS-ID: m5-preclear-base-index-producer

Session 3545 selected `H-PortWrongDestination`: retail and port both executed
the texture-record family in title and hangar, but their record base/index
contexts and effective destinations differed. Do not repeat that capture.

Do exactly one bounded work unit: instrument the producer/caller immediately
before the divergent base/index values are formed in the generated function
containing `0x8001FACC`–`0x8001FD2C`, then run one independent retail execution
watch and one same-build real-audio port capture. Keep all audio, PCM,
image-task, output, and texture-record writes unchanged.

Competing hypotheses and discriminator:

- `H-ProducerParity`: producer inputs/returns match and the remaining gap is
  earlier than the producer.
- `H-ProducerDivergence`: the first producer input, computed base, or index
  differs before the family stores.
- `H-RetailOnlyFamily`: retail executes this family in the target phase but the
  port does not; the observed port rows belong to a different route/use.
- `H-CaptureInvalid`: whole-RDRAM and both phase controls or the paired family
  witnesses are absent.

The single discriminating table must include producer PC/caller, phase/VI,
producer inputs/returns, computed base/index, and the first family store. A
matching producer tuple selects `H-ProducerParity`; a first differing input or
computed base/index selects `H-ProducerDivergence`; a retail-only execution
selects `H-RetailOnlyFamily`; missing controls select `H-CaptureInvalid`.

Before building, retain `scratch/agent/retail_preclear_groundtruth.log` and
read the existing destination injection in `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
Batch the instrumentation, then build and run both oracle and port arms in one
iteration. Use VI phase gates, SIGKILL cleanup, and capture under:

    scratch/agent/s3545_m5_destination_contract
