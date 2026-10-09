# Next work unit (s4448): why does the port's musyxRenderVoiceSamples allocate for all 31 voices (0x801951B8 + i*0x88) when retail never touches the allocator list?

HYPOTHESIS-ID: m5-ai-event-cadence

Known (s4447): callers are 4 jal sites inside musyxRenderVoiceSamples (0x8008FFAC); ra is uninformative (recomp omits r31 on jal); 31 voices round-robin, one sp frame.
Hypotheses: (a) port voices carry a "active/needs-stream" flag set that retail has clear (port-induced init or key-on); (b) retail skips musyxRenderVoiceSamples entirely in title (synth frame gated); (c) retail runs it but fill early-outs on a range check.
Discriminator: in one build dump voice words [0..0x88) for voices 0..30 at fill entry (first 31 calls) in port; oracle: read-watch (not exec) on voice 0 base 0x801951B8 phys 0x001951B8..+0x88 to see if retail reads it at all (positive control: whole-RDRAM watch). Reads present => (c)/(a); zero reads => (b).
