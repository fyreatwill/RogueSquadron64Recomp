# NEXT work unit (s2204) — compare port VI commit tuple to retail context

HYPOTHESIS-ID: m5-a1-port-vi-context-parity

## Work unit

The retail context join is now positive at a no-overflow scope: the context
selected by `__osViNext` plus `VI_CURRENT_REG & 1` produces both target origins.
Add one env-gated, phase-scoped diagnostic at the port's
`lib/N64ModernRuntime/ultramodern/src/events.cpp::ViState::update_vi` commit
point. For every width-640 commit, log one complete row containing:

`arm`, phase ordinal, `cur_state`, selected `field`, selected next-state
`state`, framebuffer physical address, guest mode pointer, both field
origins/yScales, `framebuffer + fld0.origin`, `framebuffer + fld1.origin`,
and committed origin. Emit a small all-width positive-control prefix and a
bounded per-arm summary; cap printed 640 rows at 256. Preserve the existing
`ROGUESQ_VI_ALTERNATE_FIELDS` behavior and do not make the knob default-on.
If the logger needs a host callback or guest mode pointer field, add only the
diagnostic plumbing and export submodule patches in the same iteration.

Build once, then run baseline and `ROGUESQ_VI_ALTERNATE_FIELDS=1` arms
concurrently with the same qualified recipe (`SPIN_YIELD=1`,
`LLE_UNGATED=1`, `LLE_SOLO=1`). Phase-gate collection on the first 640 entry;
collect until each arm either reaches the target-origin window or its
watchdog expires. Keep the existing `[phase]` and route controls in both logs.

## Competing hypotheses and discriminator

- H-PortFieldSelector: both arms have the retail frame/mode tuple; baseline
  commits only candidate0/`0x00696100`, while the opt-in arm selects candidate1
  and reaches `0x00696600`.
- H-PortStateTuple: one or more port framebuffer, mode-field, or state values
  differ from the retail context, so candidate sums do not reproduce the
  retail target origins in either arm.
- H-PortCommitOrdering: the port has the retail candidate values, but the
  selected field/state is committed at the wrong point relative to screen
  consumption; the candidate row and committed-origin row diverge or the
  alternate arm reaches the target only after an ordering change.

The discriminator is one same-build two-arm table with positive-control rows,
both arms' 640 commit rows, target-origin counts, zero row overflow, and the
complete tuple above. H-PortFieldSelector is selected only if the control arm
shows candidate0/first-origin rows and the alternation arm shows candidate1 /
second-origin rows with matching framebuffer/mode fields. H-PortStateTuple is
selected if the candidate tuple differs before the field choice. H-PortCommit-
Ordering is selected if both candidate sets match retail but the committed
origin or phase transition does not follow the selected candidate. A null is
invalid unless the logger's positive-control prefix and the 640 phase controls
fire in that same arm.

## Exact commands

```sh
# After implementing the single logger and exporting any lib/ patch:
./submodule-patches/export.sh
cmake --build build -j8

# Use a self-contained concurrent runner from the repository root. It must
# start both arms from build/, phase-gate on [phase] 640, collect the complete
# table, SIGKILL each process after its target window/watchdog, and fail on
# [CRASH]/[ABORT]. The two logs are:
# scratch/agent/s2204_port_vi_context/control.log
# scratch/agent/s2204_port_vi_context/alternate.log
zsh scratch/agent/run_s2204_port_vi_context_ab.sh

# Summarize only the bounded controls, phase rows, per-arm summaries, and
# candidate/committed-origin matrices:
rg -n "vi-context-port|\[phase\]|vi-context-port-summary|\[CRASH\]|\[ABORT\]" \
  scratch/agent/s2204_port_vi_context/*.log
```

Do not add a port guard, mitigation, task rewrite, or audio default change.
