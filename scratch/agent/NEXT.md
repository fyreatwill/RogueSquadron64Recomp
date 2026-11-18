# NEXT (s7590)
HYPOTHESIS-ID: host-resource-growth-audit

Class HR closed s7589 (H-flat steady state). Residual: Mach ports step +10 per hangar re-entry load (696/706/716) and +38/+39 on a
new-content load; IOAccel regions +4..+19 per load. Bounded, but the owner is not named. HR-2 names it.
Hypotheses: H-cache (ports belong to per-content caches: RT64 shader/pipeline objects, so a reload of the SAME mission adds 0),
H-leak (every load adds ~10 whatever the content, e.g. a per-load thread/semaphore/dispatch source that is never destroyed),
H-dead (dead names pile up: send rights to destroyed ports never deallocated).
Instrument, no game rebuild: extend tools/s7589_hrplant.dylib (or a sibling tools/s7590_portcensus.dylib) with a census thread that
every 10 s calls mach_port_names() on mach_task_self() and logs counts by type (RECEIVE, SEND, SEND_ONCE, PORT_SET, DEAD_NAME), plus
for the names new since the previous census: mach_port_get_refs and, for receive rights, mach_port_get_attributes (MACH_PORT_LIMITS_INFO
/ STATUS). Run the plant leak in the same process as the positive control (each leak = +1 RECEIVE, thread port shows as SEND).
Route: one mission reloaded >=4 times (hangar abort -> SELECT YOUR CRAFT -> same mission; the s7469 AP schedule picks a different
mission each time: a0 0xB1/0xB5/0x19/0x4A; drop the left/down cursor moves so the same entry is chosen), then 1 new mission.
Outcome: per-load step 0 on same-mission reloads -> H-cache (close); >0 by RECEIVE/SEND -> H-leak, name the creator (lldb breakpoint on
mach_port_allocate / semaphore_create / dispatch_source_create gated to the load window, backtrace) and fix env-gated (=0 old);
step in DEAD_NAME -> H-dead.
Sampler: tools/s7589_hrsample.zsh <out> <s> 10; scorer tools/s7589_hr_report.py --windows <plateaus>.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Key-driven route: check HID idle and
CGSSessionScreenIsLocked first, or queue it as a soak with # SOAK_NEEDS_IDLE=300.
