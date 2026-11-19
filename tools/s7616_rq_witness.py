"""s7616 class RQ runtime witness (lldb). Breakpoints with auto-continue on every RT64 function that reads/writes guest
RDRAM (readers) plus RT64's own worker-thread entry points (controls: they MUST be seen on non-Gfx threads, proving the
instrument attributes threads). Counts hits per (function, thread name). Default recipe (no RDP_ASYNC) => every reader
hit must be on "Gfx Thread". Usage (from build/):
  (start the game normally first; NEVER launch it under lldb)
  lldb --batch -o 'command script import ../tools/s7616_rq_witness.py' -o 'rq_run 60 ../scratch/s7616/witness.txt <pid>'"""
import lldb, time, collections, os, sys
C = collections.Counter()
READERS = ["RT64::State::fullSync()", "RT64::State::updateScreen", "RT64::State::checkRDRAM()",
           "RT64::State::fullSyncFramebufferPairTiles", "RT64::RDP::loadTLUT(", "RT64::RDP::loadTileOperation(",
           "RT64::RDP::loadBlockOperation(", "RT64::RDP::loadTLUTOperation(", "RT64::RDP::setColorImage(",
           "RT64::FramebufferStorage::store(", "RT64::TextureCache::queueGPUUploadTMEM(",
           "RT64::Application::processDisplayLists(", "RT64::Application::updateScreen()"]
REGEX_READERS = [r"^RT64::State::fullSync\(\)::\$_[0-9]+::operator\(\)"]
CONTROLS = ["RT64::WorkloadQueue::threadRenderFrame(", "RT64::PresentQueue::threadPresent(",
            "RT64::TextureCache::useTexture(", "RT64::BufferUploader::submit("]  # per-frame bodies of RT64's own threads
BPN = {}

def cb(frame, bp_loc, d):
    t = frame.GetThread()
    fn = BPN.get(bp_loc.GetBreakpoint().GetID(), "?")  # label by breakpoint (frame names are inlined helpers)
    C[(fn, t.GetName() or "tid%d" % t.GetThreadID())] += 1
    return False

def dump(out):
    with open(out, "w") as f:
        for (fn, th), n in sorted(C.items()):
            f.write("%s\t%s\t%d\n" % (fn, th, n))

def rq_run(debugger, command, result, d):
    a = command.split()
    secs, out = int(a[0]) if a else 60, (a[1] if len(a) > 1 else "../scratch/s7616/witness.txt")
    debugger.SetAsync(True)
    tgt = debugger.CreateTarget("./RogueSquadron64Recomp")
    nbp = 0
    for n in READERS + CONTROLS:
        bp = tgt.BreakpointCreateByRegex("^" + n.replace("(", r"\(").replace(")", r"\)").replace("$", r"\$"))
        BPN[bp.GetID()] = n; bp.SetScriptCallbackFunction("s7616_rq_witness.cb"); nbp += bp.GetNumLocations()
        print("bp %-48s locs=%d" % (n, bp.GetNumLocations()))
    for rx in REGEX_READERS:
        bp = tgt.BreakpointCreateByRegex(rx); BPN[bp.GetID()] = rx; bp.SetScriptCallbackFunction("s7616_rq_witness.cb")
        print("bp %-48s locs=%d" % (rx, bp.GetNumLocations()))
    # ATTACH only (s7616): an lldb-LAUNCHED game could not read build/rs64.n64.us.1.0.z64 and tried to delete it (EPERM saved it).
    err = lldb.SBError(); p = tgt.AttachToProcessWithID(debugger.GetListener(), int(a[2]), err)
    print("attach", err.Success(), err.GetCString(), "state", p.GetState()); sys.stdout.flush()
    debugger.HandleCommand("process handle -p true -s false -n false SIGSEGV SIGBUS SIGUSR1 SIGUSR2 SIGPIPE SIGALRM")
    # async event loop (the only form that counted on this lldb: sync + auto-continue and tight state polling both
    # stalled after 1 hit, s7616). Each stop is resumed here; the counts are a SAMPLE of hits, attributed per thread.
    p.Continue()
    lis = debugger.GetListener(); ev = lldb.SBEvent(); t0 = time.time(); stops = 0
    while time.time() - t0 < secs:
        lis.WaitForEvent(1, ev)
        st = p.GetState()
        if st == lldb.eStateStopped:
            stops += 1
            th = p.GetSelectedThread()
            if th.GetStopReason() in (lldb.eStopReasonSignal, lldb.eStopReasonException):
                print("STOP", th.GetStopDescription(200), th.GetName())
            p.Continue()
        elif st in (lldb.eStateExited, lldb.eStateCrashed, lldb.eStateDetached):
            print("process ended state", st); break
        if stops % 50 == 0: dump(out)
    dump(out); p.Kill()
    print("rows", len(C), "stops", stops, "->", out)

def __lldb_init_module(debugger, d):
    debugger.HandleCommand("command script add -f s7616_rq_witness.rq_run rq_run")
