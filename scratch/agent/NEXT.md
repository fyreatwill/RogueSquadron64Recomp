# NEXT: audit the producer of FE98's port-only ASCII cart tag
HYPOTHESIS-ID: m5-audio-destub
Completed this iteration: the retail oracle reached VI origin `0x006AB400` at width 512 and wrote B0xxxxxx pointers at the target; the corrected three-arm port watch reached the same phase, passed `[s4569-control]` in all arms, and the independent `[s4532-fill]` probe showed `site=FE98 dev=0x6C637265 size=0x300` in all arms. H-port-writer is selected over H-key-unresolved. The generic s4569 `val` field is not evidence because the parity helper supplies zero.

Run next: perform one bounded static audit of `0x8008FE98` and its caller/input chain in the current generated source and companion decomp. Identify every writer/initializer of the `t0+8` field that becomes `dev`, and classify whether the ASCII `lcre` is a legitimate resource key or a port-only fallback/translation. Do not rerun the store watch or add another value field unless this audit cannot resolve the producer.
