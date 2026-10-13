# Next work unit

HYPOTHESIS-ID: H-hangar-rdp-diff

Target (chosen by the unblock iteration, s4730): port hangar render artifacts (rim band, blue holo spikes, right-edge garbage). Retail reference EXISTS: rs64-oracle/s4514_rdp_hangar512.bin (166 MB retail hangar RDP capture, ~1244 tris/205 KB RDP per frame) and the oracle with a video plugin (rice) renders retail hangar frames.

Hypotheses for the artifact source:
- H-rdp-cmd-diff: port RDP command stream for the entry frame differs from retail (geometry/matrix/combiner words); localized by per-command diff of one phase-gated hangar frame.
- H-tex-upload: command stream matches but TMEM/texture source data differs (DXT/tex decode, s23 notes); artifacts originate in data, not game logic.
- H-renderer: command stream and RDRAM textures both match; defect is in the RT64 macOS/Metal backend.

Discriminator: dump the port's hangar-512 RDP list for the first frame after VI 0x006AB400 with the same dump tool used for s4514, diff against retail command-by-command (first divergence), phase-gated on the VI transition. Positive control: diff retail vs itself (zero divergence) and retail vs title frame (nonzero).
