# Session 3180 generated-symbol rename

The required high-address band `0x80170000..0x80180000` was empty: its helper
selection returned no generated references. A bounded follow-up synchronized
two known non-callable records:

- `static_3_80007064` -> `data_gap_80007064`
- `fake_func_800AE3E4` -> `data_gap_800AE3E4`

The second record is an 8-byte fragment ending at `0x800AE3EC`, where the
companion-qualified `tickEasedCameraKeyframeBlend` body begins. The helper
reported 3 changed references in 3 generated files, and `py_compile` passed.
The generated tree is a sibling repository; the tracked regeneration map in
this repository records the new mapping for future regeneration. No runtime
behavior changed.
