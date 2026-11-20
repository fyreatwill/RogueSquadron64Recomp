#!/bin/sh
# s7725: offline witness for the 2026-11-18-014353 "RT64 Present" SIGTRAP (brk #0xc472 = isa pointer-auth failure in
# object_getClassName <- AutoreleasePoolPage::autoreleaseNoPage <- objc_autoreleasePoolPush+72). Push first flushes the object
# parked in the TLS deferred-autorelease slot (0x160); if that object was already freed, the flush touches a dead isa.
# Arms (one tiny MRC binary, a pool-less pthread like every RT64 worker):
#   push_plain : first pool push, no debug env                         -> rc 0
#   push_debug : first pool push, OBJC_DEBUG_MISSING_POOLS=YES        -> rc 0  (the env ALONE does not trap: s7587's
#                                                                         "instrument artifact" reading is refuted)
#   overrel    : +0 objc_autoreleaseReturnValue object released by the MRC caller, then push, no env -> killed by a signal
#                (positive control: a freed pending object crashes the push even without any debug env)
# rc 0 = all three as stated; rc 1 otherwise.
set -u
D=${1:-scratch/s7725}; mkdir -p "$D"
cat > "$D/repro.m" <<'C'
#import <Foundation/Foundation.h>
#include <pthread.h>
#include <stdlib.h>
extern id objc_autoreleaseReturnValue(id);
static int mode;
__attribute__((noinline)) static id make(void) { id o = [[NSObject alloc] init]; return objc_autoreleaseReturnValue(o); }
static void *body(void *a) { (void)a; if (mode == 1) { id x = make(); [x release]; }
  NSAutoreleasePool *p = [[NSAutoreleasePool alloc] init]; [p release]; return 0; }
int main(int c, char **v) { mode = c > 1 ? atoi(v[1]) : 0; pthread_t th; pthread_create(&th, 0, body, 0); pthread_join(th, 0); return 0; }
C
clang -fno-objc-arc -O0 -framework Foundation "$D/repro.m" -o "$D/repro" || { echo "s7725 build FAIL"; exit 1; }
"$D/repro" 0 >/dev/null 2>&1; P=$?
env OBJC_DEBUG_MISSING_POOLS=YES "$D/repro" 0 >/dev/null 2>&1; G=$?
"$D/repro" 1 >/dev/null 2>&1; O=$?
echo "s7725 push_plain_rc=$P push_debug_rc=$G overrel_rc=$O"
if [ $P -eq 0 ] && [ $G -eq 0 ] && [ $O -gt 128 ]; then echo "s7725 VERDICT freed-pending-object (CONTROL PASS)"; exit 0; fi
echo "s7725 VERDICT not-confirmed"; exit 1
