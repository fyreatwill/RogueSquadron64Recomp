# Next work unit: qualify the M3 sentinel/cursor guard

HYPOTHESIS-ID: m3-sentinel-cursor-ownership

Competing hypotheses and discriminator written before the build:

- H-sentinel-alias: `heap_bump` can equal the active sentinel, allowing the
  allocator cursor to publish queue metadata as a new allocation.
- H-clean: valid allocator state never aliases the sentinel; the guard is
  inert on valid behavior.
- H-toolchain-block: the source change is valid, but missing MIPS GCC/LD
  prevents patch ELF/runtime qualification.

The discriminator is source inspection plus one ordinary Debug build and one
patch-target availability check. The new guard must reject only
`heap_bump == *heap_tail_loc`; the ordinary target must build; and the patch
target must either build or report the concrete missing toolchain. No runtime
claim is valid without PatchesLib.

ORIGIN: `heap_bump` is published by the allocator after dequeue, while
`heap_tail_loc` publishes the active sentinel. The sentinel is metadata, not a
legitimate next-block cursor.

Next iteration: if a MIPS toolchain is supplied, build `PatchesLib`, run the
existing qualified route, and exercise the guard with the patch/runtime
controls. If it remains unavailable, audit the next complete allocator
ownership idiom rather than repeating a route capture.
