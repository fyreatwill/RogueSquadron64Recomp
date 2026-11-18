# NEXT (s7602)
HYPOTHESIS-ID: toptr-host-typed-guest-view-census

Class BS closed s7601 (522 raw-view sites, 0 open, 0 BAD on default paths, controls 4/4; tools/s7601_bs_census.py). Its
residual: guest memory dereferenced as a HOST TYPE through TO_PTR(T, x) / _arg<N, PTR(T)> / helpers.hpp, where only 6 struct
types were layout-checked (STRUCTS in s7601_bs_census.py).

Class TP = every TO_PTR / _arg<PTR(T)> / reinterpret_cast<T*>(TO_PTR...) site in librecomp/src, ultramodern/src, src/ (skip
tests/tools). Per site name T and classify:
  word        T is 32-bit scalar or a struct of only 32-bit members (OSMesgQueue, OSTask, OSTimer?, OSMesg) -> ok
  swizzled    struct with sub-word members, every one pre-swapped (add T to s7601 STRUCTS and let struct_check prove it)
  consumer    sub-word scalar/array (u8/char/int16_t/void) whose consumer applies ^3 / ^2 or swaps (named, e.g. audio
              queue_samples int16 pairs, string reads via MEM_B)
  gated       diagnostic
  BAD         sub-word access with no swizzle on a default path
Known leads to check first: cont.cpp:58 PTR(OSContPad) (6-byte struct, button u16 + 2 s8 + u8 NOT pre-swapped in ultra64.h,
and arrays of it straddle words: how does osContGetReadData write it?), PTR(u8)/PTR(char) args (strings from guest), ai.cpp:88
TO_PTR(uint8_t) audio buffer, audio.cpp TO_PTR(int16_t), OSPfs id/label "funky endianness" TODO, OSTimer layout.
Hypotheses: H-clean (all swizzled/consumer), H-bad (a default-path sub-word view reads wrong bytes: e.g. controller stick
axes swapped would show as wrong input), H-gated.
Tool: tools/s7602_tp_census.py --controls (plant `TO_PTR(uint16_t, a)[0]` read into a copy of cont.cpp -> OPEN; drop a row ->
OPEN; extend STRUCTS check to OSContPad and plant a swapped member -> BAD).
Runtime witness for any BAD row: known-value test (write a known guest pattern via MEM_* in a host unit, read via the view),
plus, if controller-facing, a keyed run reading the guest-visible pad bytes (ROGUESQ_FORCE_* recipe, copied save folder).
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
