# NEXT: build the per-invocation EBC join fix
HYPOTHESIS-ID: g1c-dd8-limit

One bounded change: replace the s6500 cumulative counter delta with a
regeneration-safe sequence/key captured at the bin return and matched at
stream entry/writer time. Preserve the writer census and emit a delta only for
a matching interval; do not change game behavior.

The s6505 audit is in `docs/S6505-EBC-WRITER-AUDIT.md`: H-duplicate and
H-uninstrumented are refuted; H-boundary is selected.

Competing hypotheses and discriminator for the one build/run:

- H-boundary: a keyed interval makes EBC deltas monotonic and removes the
  underflow while retaining dd1 nonempty and dd4 EMPTY writer activity.
- H-race: a keyed/serialized snapshot still underflows or loses increments,
  proving shared host-thread mutation remains.
- H-missing: matched rows show EBC table changes without the keyed writer,
  proving an uninstrumented writer remains.

Apply the fix through the existing s650 fixup path, build once, and run:

    zsh scratch/agent/s6492_forface.sh

Require dd1 nonempty controls, dd4 EMPTY controls, and a positive key-match
control. No soak is justified until the key discriminator passes.
