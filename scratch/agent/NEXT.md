# Next work unit: restore the title->hangar key route, then rerun the mission census
HYPOTHESIS-ID: patcheslib-shadowed
s5371 soak: nohangar t=200 (title reached, hangar never). Earlier soaks s5094/s5099 reached hangar the same day. Hypotheses: H1 winctl focus/key timing broke (host load/focus), H2 a build change altered behaviour before hangar, H3 route flake. Discriminator: rerun s5099 recipe verbatim as positive control; if it reaches hangar, diff its env vs s5371 COMMON (s5371 adds LOG_ALLOC_TAIL_GUARD2/3, LOG_M5_ROUTE_TRANSITION, LOG_PCM_BOUNDARY, AUDIO_UCODE, DLWALK, PROBE_LEAVE_OK).
Needs human decision first: see BLOCKED.md.
