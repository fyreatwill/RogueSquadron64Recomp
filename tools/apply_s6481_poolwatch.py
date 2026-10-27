"""s6481 G1c: write-watch on the 12-byte node pool at *0x80136FCC (allocAndInitDoublyLinkedNodePool12). Hooks the existing
per-store helper rs64_probe_submit_gate_store: tracks the pool base from the 0x80041F24 store, then for every halfword store to
row+2 (the 'next' link) logs (pc,row,value,phase). Init-loop stores (pc 0x80041F48) are only counted. Gate: ROGUESQ_POOLWATCH=1.
Per-(pc,value==FFFF) counts are printed every 2048 events so the run carries a histogram. Idempotent."""
TAG = "PATCH: s6481 poolwatch"
ANCHOR = '    static int enabled = -1;\n    static int control = 0;\n    static unsigned long rows = 0;\n'
NEW = '''    { /* ''' + TAG + ''' */
      static uint32_t pw_en = 2; extern uint32_t g_s6481_pool;
      if (pw_en == 2) { const char* e = getenv("ROGUESQ_POOLWATCH"); pw_en = (e && e[0] && e[0] != '0') ? 1 : 0; }
      if (pw_en) {
        if (width == 'W' && addr == 0x80136FCCu) { g_s6481_pool = value; fprintf(stderr, "[poolwatch] base=%08x pc=%08x\\n", value, pc); }
        uint32_t b = g_s6481_pool;
        if (b && width == 'H' && addr >= b && addr < b + 12u * 8000u && ((addr - b) % 12u) == 2u) {
          extern uint32_t rs64_phase_ord(void);
          static uint32_t ev = 0, shown = 0, initn = 0, nonff = 0, ff = 0; static uint32_t pcs[16], pcn[16], pcf[16]; static int npc = 0;
          uint32_t row = (addr - b) / 12u; uint32_t v = value & 0xFFFFu; ev++;
          if (pc == 0x80041F48u) { initn++; if (row == 0 || row == 5 || row == 100) fprintf(stderr, "[poolwatch] init row=%u v=%u phase=%u (initn=%u)\\n", row, v, rs64_phase_ord(), initn); }
          else {
            int k = 0; for (; k < npc; k++) if (pcs[k] == pc) break;
            if (k == npc && npc < 16) { pcs[npc] = pc; pcn[npc] = 0; pcf[npc] = 0; npc++; }
            if (k < 16) { if (v == 0xFFFFu) pcf[k]++; else pcn[k]++; }
            if (v == 0xFFFFu) ff++; else nonff++;
            if (shown < 300) { shown++; fprintf(stderr, "[poolwatch] w pc=%08x row=%u v=%04x phase=%u\\n", pc, row, v, rs64_phase_ord()); }
            if ((ev & 0x3FFu) == 0) { fprintf(stderr, "[poolwatch] hist ev=%u init=%u nonFFFF=%u FFFF=%u phase=%u:", ev, initn, nonff, ff, rs64_phase_ord());
              for (int j = 0; j < npc; j++) fprintf(stderr, " %08x(%u/%u)", pcs[j], pcn[j], pcf[j]); fprintf(stderr, "\\n"); }
          }
        }
      }
    }
'''
HELPER_DEF = 'uint32_t g_s6481_pool __attribute__((weak));\n'
def apply_helper(t):
    if TAG in t or ANCHOR not in t: return t, 0
    t = t.replace(ANCHOR, NEW + ANCHOR, 1)
    t = t.replace('static int s_process_scene_node_depth;\n', 'static int s_process_scene_node_depth;\n' + HELPER_DEF, 1)
    return t, 1
