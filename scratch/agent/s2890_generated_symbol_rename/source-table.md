# s2890 generated-symbol sweep: `0x800FBE14..0x800FEF0F`

| Candidate | Project span and neighbors | Generated body | Companion/call evidence | Selection |
|---|---|---|---|---|
| `0x800FBE14` (`fake_func_800FBE14`) | 12 bytes; immediately after the complete `advanceMissionObjectiveStageWhenModeOne` body and before `configurePlayerSecondaryWeaponHud` at `0x800FBE20` | Three data-decoded words: invalid `0x73742021`, a discarded `lui`, and invalid `0x4C4C0000`; no prologue, return, or callable entry | Companion map supplies no semantic name; no independent caller or exact source definition found | H-DataGap → `data_gap_800FBE14` |
| `0x800FEF04` (`fake_func_800FEF04`) | 12 bytes; immediately after `getHudSecondaryWeponCount` ending at `0x800FEF00` and before `stepObjectOrientationTowardTarget` at `0x800FEF10` | Fixup-generated `__builtin_trap()` gap body; source bytes are invalid data | Companion map supplies no semantic name; no independent caller or exact source definition found | H-DataGap → `data_gap_800FEF04` |

Both records are bounded non-callable fragments. H-Callable and H-Ambiguous
were rejected; the following unresolved project placeholder is `0x80101CCC`.
