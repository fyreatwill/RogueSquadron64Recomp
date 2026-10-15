# cxd4 RSP per-task VACC/DMEM dump (s5003)

Tree: ~/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4 (not a git repo). Build: `cd projects/unix && make all`.
Recipe: scratch/agent/s5003_cxd4_dump.sh (enable with RS64_RSP_DUMP=<path>).
Record (4156 B): "RSD1", seq u32, task_type u32 (1=gfx, 2=audio), VACC[3][8] i16 (rows LO/MD/HI), DMEM 4096 B.

Edit to module.c: insert before `DoRspCycles`, and call `rs64_rsp_dump((u32)task_type);` right after `run_task();`.

```c
static void rs64_rsp_dump(u32 task_type)
{
    static FILE* f; static int init; static u32 seq;
    if (!init) {
        const char* p = getenv("RS64_RSP_DUMP");
        init = 1;
        if (p) f = fopen(p, "wb");
    }
    if (!f) return;
    fwrite("RSD1", 1, 4, f); fwrite(&seq, 4, 1, f); fwrite(&task_type, 4, 1, f);
    fwrite(VACC, sizeof(i16), 3 * 8, f);
    fwrite(DMEM, 1, 4096, f);
    fflush(f);
    seq++;
}
```
