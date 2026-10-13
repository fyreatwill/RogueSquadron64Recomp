# RESUME — next work unit: compile the already-landed Factor 5 overlay-0x2C image

HYPOTHESIS-ID: factor5-overlay-0x2c-splice

The s4772 static census closes the shutdown-only branch: one guarded caller
exists and no alias/wrapper reference was found. The next actionable unit is
the already-landed 0x2C RSP image splice, but its compiler invocation needs the
human Bash allow rule in `scratch/agent/UNBLOCK.md`.

Competing hypotheses and discriminating measurement:

- H2C-real-image: compiling and splicing overlay `0x2C` supplies the missing
  `TexrectGen` implementation and removes the mission DL restart loop.
- H2C-route-unrelated: the image compiles and dispatches, but the runaway loop
  persists, so the loop has another cause.
- H2C-output-neutral: the loop ends but ship/HUD pixels do not change, so the
  overlay is not the visible-content blocker.

DISCRIMINATING MEASUREMENT: an allowlisted RSPRecomp run must emit the 0x2C
recompiled C, followed by one phase-gated mission run with the existing 0xBD,
overlay-arrival, DL-restart, and ship/HUD controls. Compile failure leaves the
unit blocked on the allow rule; compiled image plus no restart selects
H2C-real-image; compiled image plus restart selects H2C-route-unrelated; a
clean loop with unchanged output selects H2C-output-neutral.

Commands:

```sh
# After the human allow rule is added, run the exact command in UNBLOCK.md.
sed -n '1,220p' scratch/agent/UNBLOCK.md
python3 tools/assemble_factor5_overlay_0x2c.py
env PROBE_PHASE_WIDTH=1 PROBE_KEYS_FROM_PHASE=1 zsh scratch/agent/run_overlay_0x2c_validation.sh
```

Do not change callback deregistration or add a shutdown mitigation. If the
compiler remains blocked, write BLOCKED.md with the exact denied command and
the one allow-rule change needed.
