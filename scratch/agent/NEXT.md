# Next work unit: rerun the s5371 mission path census using the interactive-launch hangar route
HYPOTHESIS-ID: patcheslib-shadowed
s5375: current 18:30 binary reaches hangar 2/2 when launched via scratch/agent/bisect_hangar.sh from a shell (soak s5373 got 0/2). So the build is fine; soak-runner context loses focus/keys (suspect: winctl activate under loop's process group).
Next: (1) run `zsh scratch/agent/bisect_hangar.sh RogueSquadron64Recomp 5` for n=5 and compare to a queued soak of the same recipe: if interactive >=4/5 and soak 0/N, fix soak focus handling (positive control: key press changes title). (2) Then redo the s5371 mission census with the working route.
Outcomes: interactive high + soak low => runner focus issue; both low => flaky route, add retries.
