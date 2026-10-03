# s3748 M5 native host writer-PC watch

The remaining computed-pointer/external-host-write class was tested with a
macOS ARM64 `mprotect` write-fault watch. The watch protected the native page
containing physical `0x128C92` and `0x128CD0..0x128CD3`, recovered each fault,
and captured the host ARM64 PC and fault address. It was enabled in one build
and run concurrently with real-audio and silent port arms.

## Result

Both port arms reached the qualified title and hangar phases. The watch's
positive-control path fired in both arms on a non-exact write (`0x128D2F` in
real and `0x128004` in silent), proving the native fault handler and page
protection were live. Neither arm produced an exact-field fault row in the
target phases. There were no crash or abort markers.

The independent retail oracle passed its whole-RDRAM control, reached title
`0x00790400`/1024 and hangar `0x006AB400`/512, and independently observed the
known retail write at `0x128CD0` from guest PC `0x8001BB14`; its neighboring
`0x128C90` write was also observed. This validates that the exact physical
watch span is active on the retail route, while the port watch tests native
host ownership rather than guest writer parity.

## Interpretation

This selects `H-ExactFieldUnwritten` for the remaining arbitrary native host
write class in the qualified port capture. It does not select a producer for
the image source: `H-RouteStateNotSource` remains open because the exact route
fields may be control metadata rather than the source payload.

ORIGIN: diagnostic-only macOS ARM64 page-fault attribution. No mitigation or
value suppression was added; the existing zero-fill writer `0x800078EC` was
unchanged.

Evidence: `scratch/agent/s3748_m5_host_writer_fault/{real,silent,oracle}.log`
and `summary.txt`; implementation is in `src/main/main.cpp` under
`ROGUESQ_LOG_M5_HOST_WRITE_FAULT`.
