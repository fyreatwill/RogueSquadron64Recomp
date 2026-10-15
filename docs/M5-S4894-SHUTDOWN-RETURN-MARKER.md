# M5 s4894 — shutdownAudioEngine return marker

The Debug target was rebuilt after adding the regeneration-replayable
`s4894` marker immediately before the generated `shutdownAudioEngine` return.
The marker calls the existing callback teardown host witness with `kind=2`;
the existing function-entry witness uses `kind=0`, while callback registration
uses `kind=1`.

The qualified real-audio/LLE/ungated/solo/spin-yield capture passed the route
controls: title VI 1024, hangar VI 512, 758 phase-gated SP completion-return
rows, 44 PCM-source rows, 259 PCM-consumer rows, and 259 audio-return rows.
There were no crash or abort rows.

The callback discriminator recorded seven `[s4771-cb]` rows, all `kind=1`,
which are registration events. It recorded zero `kind=0` shutdown-entry rows
and zero `kind=2` return rows. The independent callback-table trace still
recorded six deregistration pairs, so table activity and downstream audio work
are real, but they do not prove that `shutdownAudioEngine` ran.

Conclusion: H3 is selected for this work unit. The new marker is compiled into
the generated function, but the qualified route never reaches that function;
s4893's attribution of the seven/nine entry rows to `shutdownAudioEngine` was a
kind misread. No teardown behavior changed. A new route or callsite-specific
ground-truth discriminator is required before pursuing this exact return
boundary.

ORIGIN: diagnostic-only generated entry/return and existing callback-table,
SP, PCM, audio-return, and VI controls. No callback table, teardown, or audio
behavior changed.
