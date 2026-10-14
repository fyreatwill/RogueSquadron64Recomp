# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

s4866: retail reset:incr:store = 702:1343:702 (loop bound 2, ra 0x80091338 at reset, 0x800910b0 at incr); port 2:1:1.
Hypotheses: (H1) loop-bound halfword 0x8014974E (read at 0x800911C8) is 1 in the port, 2 in retail (upstream writer differs); (H3) port's extra reset comes from a second caller not in retail.
Discriminator: extend tools/apply_s4864_datasize_trace.py to log MEM_HU(0x8014974E) at each incr/reset and the caller ra at each reset (ROGUESQ_LOG_S4864=1); also oracle --pc-field-dump or a watch-write on physical 0x14974E to find the retail writer PC and value. Control: histogram total == store count.
