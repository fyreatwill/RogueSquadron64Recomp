# NEXT work unit (after s693 valid-DL cap capture)

HYPOTHESIS-ID: m3-e9-provenance-cap

Add one regeneration-safe, phase-scoped trace that joins each Factor 5 opcode
`0x06` (`F3DSWRS_DL`) command to its LLE saved-frame push and eventual return.
Do not add a mitigation or change decoder behavior.

## Competing hypotheses

- **H-extra-push:** opcode `0x06` takes a push path where Factor 5 semantics
  require a branch/tail path, accumulating the observed eight frames.
- **H-missing-return:** each `0x06` push is legitimate, but its matching
  EndDL/root return is skipped or resumes the wrong continuation.
- **H-game-open-chain:** the captured chain is legitimate game input and its
  depth eventually unwinds outside the bounded cap observation.

## Discriminating measurement

Instrument `0x06` decode with its command PC, w0/w1, selected push/branch
mode, depth before/after, and a monotonically paired push id; emit the paired
id and depth at EndDL/root-return. Phase-latch records at section 2 and bound
them to the first 64 cap tasks after recovery. The existing four boot
`[e9-prov]` controls plus one boot `0x06` pair must visibly complete.
Extra unmatched pushes support H-extra-push; matched pushes without root
return support H-missing-return; balanced pairs refute both and support
H-game-open-chain. Put generated-code changes in the appropriate fixup
script, then regenerate/build before running the existing phase-gated recipe.

## Commands

    rg -n '0x06|F3DSWRS_DL|L_12A0|L_10E8' build/factor5_ucode tools/fixup_factor5_ucode.py
    ~/Documents/Tools/N64Recomp/build/RSPRecomp factor5_rsp.toml
    python3 tools/make_clip_composite.py && ~/Documents/Tools/N64Recomp/build/RSPRecomp factor5_rsp_ovl4.toml
    ~/Documents/Tools/N64Recomp/build/RSPRecomp factor5_boot_rsp.toml && python3 tools/fixup_factor5_ucode.py
    export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer; cd build && cmake --build . -j8
    env BUDGET_S=2400 TARGET_PULSED=1 SEC2_SETTLE_S=8 POST_PULSE_HOLD_S=15 MAX_HOLD_S=45 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh
