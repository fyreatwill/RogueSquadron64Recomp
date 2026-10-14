# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

s4873: host VI thread is the sole poster (1 msg/VI), yet the guest retrace callback walk (synth 0x8009123C) runs 2x per VI message in the port; retail ~1 walk per ~1.91 AI-done.
Hypotheses: (H-RECV) osRecvMesg shim returns twice per message / spurious wake; (H-LOOP) handler loop re-walks callbacks without blocking; (H-RETAIL) retail also walks 2x per VI message.
Discriminator: fixup-script patch in viRetraceHandlerThread (funcs_4.c ~36424): per walk log recv return, msg value, queue ptr, blocked?; retail twin: oracle exec count 0x80019B74 vs VI count. 2 recvs per msg -> H-RECV; 1 recv per walk w/o block -> H-LOOP; retail also 2 walks/msg -> H-RETAIL.
Reuse: scratch/agent/run_s4875_{base,hz115,trace}.sh.
