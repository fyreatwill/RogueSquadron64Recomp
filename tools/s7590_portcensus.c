// s7590 HR-2 in-process Mach port census, injected with DYLD_INSERT_LIBRARIES (no game rebuild).
// Every RS64_PC_S seconds (default 10) a thread calls mach_port_names(mach_task_self()) and groups every name by a key:
//   <rights>/<kobject>/<what>   rights = R (receive) S (send) O (send-once) P (port set) D (dead name), combined e.g. RS
//   kobject = mach_port_kobject_description type (-1 = plain user port, 1 thread, 2 task, 23 semaphore, 30 IOKit object, ...)
//   what    = IOKit class from the kobject description, or for user ports the creator recorded by the interposed allocators
//             (mach_port_allocate / mach_port_construct / mach_reply_port / semaphore_create / IOServiceOpen): first
//             non-system frame symbol + immediate caller; "unattr" when the name arrived another way (MIG reply, xpc).
// Output (RS64_PC_OUT, default /tmp/rs64_portcensus.log): "C t=<s> total= R= S= O= P= D=" per tick, then "K <key> n=<count>
// d=<delta>" for every key whose count changed (all keys on the first tick), then "NEW <key> <n>" for names absent last tick.
// Positive control: RS64_PC_PLANT_DELAY=<s> (>0) leaks, every 30 s after the delay, one receive port (key R/-1/s7590-plant)
// one semaphore (S/23/...) and one dead name (D/-1/unattr, via TR) -> each key must step +1 per leak. Banner "[s7590-pc]" on stderr.
#include <mach/mach.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <execinfo.h>
#include <dlfcn.h>
#include <os/lock.h>
#include <IOKit/IOKitLib.h>

extern mach_port_t mach_reply_port(void);
kern_return_t mach_port_kobject_description(ipc_space_read_t, mach_port_name_t, natural_t *, mach_vm_address_t *, char *);

#define NF 16
#define TB 32768
typedef struct { mach_port_name_t name; unsigned char used; unsigned char nf; void *f[NF]; const char *via; } rec_t;
static rec_t g_tab[TB];
static os_unfair_lock g_lk = OS_UNFAIR_LOCK_INIT;
static volatile int g_ready; // set at the end of the constructor: dyld/libSystem bring-up calls these before TLS/backtrace are usable

static void record(mach_port_name_t n, const char *via, int skip) {
  if (!n || !g_ready) return;
  void *fr[NF + 4]; int k = backtrace(fr, NF + 4);
  unsigned h = (n * 2654435761u) & (TB - 1);
  os_unfair_lock_lock(&g_lk);
  for (int i = 0; i < TB; i++) { rec_t *r = &g_tab[(h + i) & (TB - 1)];
    if (!r->used || r->name == n) { r->used = 1; r->name = n; r->via = via; r->nf = 0;
      for (int j = skip; j < k && r->nf < NF; j++) r->f[r->nf++] = fr[j]; break; } }
  os_unfair_lock_unlock(&g_lk);
}
static int lookup(mach_port_name_t n, rec_t *out) {
  unsigned h = (n * 2654435761u) & (TB - 1); int ok = 0;
  os_unfair_lock_lock(&g_lk);
  for (int i = 0; i < TB; i++) { rec_t *r = &g_tab[(h + i) & (TB - 1)]; if (!r->used) break;
    if (r->name == n) { *out = *r; ok = 1; break; } }
  os_unfair_lock_unlock(&g_lk);
  return ok;
}

// ---- interposers ----
static kern_return_t my_mpa(ipc_space_t t, mach_port_right_t r, mach_port_name_t *n) {
  kern_return_t kr = mach_port_allocate(t, r, n); if (kr == KERN_SUCCESS && t == mach_task_self()) record(*n, "mpa", 2); return kr; }
static kern_return_t my_mpc(ipc_space_t t, mach_port_options_ptr_t o, mach_port_context_t c, mach_port_name_t *n) {
  kern_return_t kr = mach_port_construct(t, o, c, n); if (kr == KERN_SUCCESS && t == mach_task_self()) record(*n, "mpc", 2); return kr; }
static mach_port_t my_mrp(void) { mach_port_t p = mach_reply_port(); record(p, "mrp", 2); return p; }
static kern_return_t my_sem(task_t t, semaphore_t *s, int p, int v) {
  kern_return_t kr = semaphore_create(t, s, p, v); if (kr == KERN_SUCCESS) record(*s, "sem", 2); return kr; }
static kern_return_t my_iso(io_service_t s, task_port_t t, uint32_t ty, io_connect_t *c) {
  kern_return_t kr = IOServiceOpen(s, t, ty, c); if (kr == KERN_SUCCESS) record(*c, "iso", 2); return kr; }
typedef struct { const void *repl, *orig; } interpose_t;
__attribute__((used, section("__DATA,__interpose"))) static const interpose_t g_ip[] = {
  { (const void *)my_mpa, (const void *)mach_port_allocate }, { (const void *)my_mpc, (const void *)mach_port_construct },
  { (const void *)my_mrp, (const void *)mach_reply_port }, { (const void *)my_sem, (const void *)semaphore_create },
  { (const void *)my_iso, (const void *)IOServiceOpen } };

// ---- census ----
static int is_sys(const char *p) { return !p || !strncmp(p, "/usr/lib/", 9) || !strncmp(p, "/System/", 8); }
static void sym(void *a, char *o, size_t on) {
  Dl_info di; if (dladdr(a, &di) && di.dli_sname) snprintf(o, on, "%s", di.dli_sname);
  else if (dladdr(a, &di) && di.dli_fname) { const char *b = strrchr(di.dli_fname, '/'); snprintf(o, on, "%s+0x%lx", b ? b + 1 : di.dli_fname, (unsigned long)((char *)a - (char *)di.dli_fbase)); }
  else snprintf(o, on, "%p", a); }
static void creator(const rec_t *r, char *o, size_t on) {
  // via:first-nonsystem-frame<-its caller ; falls back to the immediate caller chain when every frame is a system image
  int pick = -1; for (int i = 0; i < r->nf; i++) { Dl_info di; if (dladdr(r->f[i], &di) && !is_sys(di.dli_fname) && !strstr(di.dli_fname, "s7590_portcensus")) { pick = i; break; } }
  char a[160], b[160] = ""; if (pick < 0) pick = r->nf > 1 ? 1 : 0;
  if (r->nf == 0) { snprintf(o, on, "%s:?", r->via); return; }
  sym(r->f[pick], a, sizeof a); if (pick + 1 < r->nf) sym(r->f[pick + 1], b, sizeof b);
  char c0[160] = ""; if (pick > 0) sym(r->f[0], c0, sizeof c0);
  snprintf(o, on, "%s:%s<-%s%s%s", r->via, a, b, c0[0] ? "|via " : "", c0);
}

typedef struct { char key[384]; int n, prev; } kv_t;
static kv_t *g_kv; static int g_nkv, g_capkv;
static int kidx(const char *k) {
  for (int i = 0; i < g_nkv; i++) if (!strcmp(g_kv[i].key, k)) return i;
  if (g_nkv == g_capkv) { g_capkv = g_capkv ? g_capkv * 2 : 256; g_kv = realloc(g_kv, g_capkv * sizeof(kv_t)); }
  memset(&g_kv[g_nkv], 0, sizeof(kv_t)); snprintf(g_kv[g_nkv].key, sizeof g_kv[0].key, "%s", k); return g_nkv++; }
static mach_port_name_t *g_prev; static unsigned g_nprev;
typedef struct { mach_port_name_t n; int k; } nk_t; static nk_t *g_pk; static unsigned g_npk; // previous tick: name -> key index
static int cmpnk(const void *a, const void *b) { mach_port_name_t x = ((const nk_t *)a)->n, y = ((const nk_t *)b)->n; return x < y ? -1 : x > y; }
static int cmpu(const void *a, const void *b) { mach_port_name_t x = *(const mach_port_name_t *)a, y = *(const mach_port_name_t *)b; return x < y ? -1 : x > y; }

static void keyof(mach_port_name_t n, mach_port_type_t ty, char *o, size_t on) {
  char rs[8]; int q = 0;
  if (ty & MACH_PORT_TYPE_RECEIVE) rs[q++] = 'R'; if (ty & MACH_PORT_TYPE_SEND) rs[q++] = 'S';
  if (ty & MACH_PORT_TYPE_SEND_ONCE) rs[q++] = 'O'; if (ty & MACH_PORT_TYPE_PORT_SET) rs[q++] = 'P';
  if (ty & MACH_PORT_TYPE_DEAD_NAME) rs[q++] = 'D'; rs[q] = 0;
  natural_t kt = (natural_t)-1; mach_vm_address_t ad = 0; char d[512] = "";
  int kot = -1;
  if (!(ty & (MACH_PORT_TYPE_PORT_SET | MACH_PORT_TYPE_DEAD_NAME)) && mach_port_kobject_description(mach_task_self(), n, &kt, &ad, d) == KERN_SUCCESS) kot = (int)kt;
  char *p = strchr(d, '('); if (p) *p = 0;
  char w[300] = "";
  rec_t r; if (d[0]) snprintf(w, sizeof w, "%s", d);
  else if (lookup(n, &r)) creator(&r, w, sizeof w);
  else snprintf(w, sizeof w, "unattr");
  snprintf(o, on, "%s/%d/%s", rs, kot, w);
}

static FILE *g_out; static double g_t0;
static double now(void) { struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec + ts.tv_nsec / 1e9; }
static void census(int tick) {
  mach_port_name_array_t nm; mach_port_type_array_t ty; mach_msg_type_number_t nc, tc;
  if (mach_port_names(mach_task_self(), &nm, &nc, &ty, &tc) != KERN_SUCCESS) { fprintf(g_out, "C t=%.0f ERR\n", now() - g_t0); return; }
  for (int i = 0; i < g_nkv; i++) { g_kv[i].prev = g_kv[i].n; g_kv[i].n = 0; }
  int cR = 0, cS = 0, cO = 0, cP = 0, cD = 0; char key[384];
  char **newk = calloc(nc ? nc : 1, sizeof(char *)); int nnew = 0;
  nk_t *pk = malloc((nc ? nc : 1) * sizeof *pk); char **trk = calloc(nc ? nc : 1, sizeof(char *)); int ntr = 0;
  for (unsigned i = 0; i < nc; i++) {
    mach_port_type_t t = ty[i];
    cR += !!(t & MACH_PORT_TYPE_RECEIVE); cS += !!(t & MACH_PORT_TYPE_SEND); cO += !!(t & MACH_PORT_TYPE_SEND_ONCE);
    cP += !!(t & MACH_PORT_TYPE_PORT_SET); cD += !!(t & MACH_PORT_TYPE_DEAD_NAME);
    keyof(nm[i], t, key, sizeof key); { int ix = kidx(key); g_kv[ix].n++; pk[i].n = nm[i]; pk[i].k = ix;
      nk_t q = { nm[i], 0 }; nk_t *o = g_pk ? bsearch(&q, g_pk, g_npk, sizeof *g_pk, cmpnk) : 0;
      if (o && o->k != ix) { char b[800]; snprintf(b, sizeof b, "%s => %s", g_kv[o->k].key, key); trk[ntr++] = strdup(b); } }
    if (tick > 0 && !bsearch(&nm[i], g_prev, g_nprev, sizeof *g_prev, cmpu)) newk[nnew++] = strdup(key);
  }
  fprintf(g_out, "C t=%.0f total=%u R=%d S=%d O=%d P=%d D=%d keys=%d\n", now() - g_t0, nc, cR, cS, cO, cP, cD, g_nkv);
  for (int i = 0; i < g_nkv; i++) if (tick == 0 || g_kv[i].n != g_kv[i].prev)
    fprintf(g_out, "K %s n=%d d=%+d\n", g_kv[i].key, g_kv[i].n, g_kv[i].n - g_kv[i].prev);
  for (int i = 0; i < nnew; i++) { if (!newk[i]) continue; int c = 1;
    for (int j = i + 1; j < nnew; j++) if (newk[j] && !strcmp(newk[i], newk[j])) { c++; free(newk[j]); newk[j] = 0; }
    fprintf(g_out, "NEW %s %d\n", newk[i], c); free(newk[i]); }
  for (int i = 0; i < ntr; i++) { if (!trk[i]) continue; int c = 1;
    for (int j = i + 1; j < ntr; j++) if (trk[j] && !strcmp(trk[i], trk[j])) { c++; free(trk[j]); trk[j] = 0; }
    fprintf(g_out, "TR %s %d\n", trk[i], c); free(trk[i]); }
  free(trk); free(g_pk); g_pk = pk; g_npk = nc; qsort(g_pk, g_npk, sizeof *g_pk, cmpnk);
  free(newk); fflush(g_out);
  free(g_prev); g_prev = malloc((nc ? nc : 1) * sizeof *g_prev); memcpy(g_prev, nm, nc * sizeof *nm); g_nprev = nc;
  qsort(g_prev, g_nprev, sizeof *g_prev, cmpu);
  vm_deallocate(mach_task_self(), (vm_address_t)nm, nc * sizeof *nm); vm_deallocate(mach_task_self(), (vm_address_t)ty, tc * sizeof *ty);
}
static void *census_thr(void *a) {
  (void)a; const char *e = getenv("RS64_PC_S"); int s = e ? atoi(e) : 10; if (s < 1) s = 10;
  const char *pd = getenv("RS64_PC_PLANT_DELAY"); int plant = pd ? atoi(pd) : 0; int nplant = 0; double nextp = plant > 0 ? plant : 1e18;
  fprintf(stderr, "[s7590-pc] census every %d s, plant delay %d\n", s, plant);
  for (int tick = 0;; tick++) {
    census(tick); sleep(s);
    double t = now() - g_t0;
    if (t >= nextp) { // positive control: one receive port + one semaphore
      mach_port_t p = MACH_PORT_NULL; semaphore_t sm = MACH_PORT_NULL;
      mach_port_allocate(mach_task_self(), MACH_PORT_RIGHT_RECEIVE, &p);
      semaphore_create(mach_task_self(), &sm, 0, 0);
      { mach_port_t dn = MACH_PORT_NULL; // dead-name control: send right whose receive right is destroyed -> 1 D per plant
        mach_port_allocate(mach_task_self(), MACH_PORT_RIGHT_RECEIVE, &dn); mach_port_t dn2 = MACH_PORT_NULL;
        mach_port_allocate(mach_task_self(), MACH_PORT_RIGHT_RECEIVE, &dn2);
        mach_port_insert_right(mach_task_self(), dn2, dn2, MACH_MSG_TYPE_MAKE_SEND); mach_port_mod_refs(mach_task_self(), dn2, MACH_PORT_RIGHT_RECEIVE, -1);
        mach_port_mod_refs(mach_task_self(), dn, MACH_PORT_RIGHT_RECEIVE, -1); }
      os_unfair_lock_lock(&g_lk); os_unfair_lock_unlock(&g_lk);
      { unsigned h = (p * 2654435761u) & (TB - 1); os_unfair_lock_lock(&g_lk);
        for (int i = 0; i < TB; i++) { rec_t *r = &g_tab[(h + i) & (TB - 1)]; if (!r->used || r->name == p) { r->used = 1; r->name = p; r->via = "s7590-plant"; r->nf = 0; break; } }
        os_unfair_lock_unlock(&g_lk); }
      fprintf(stderr, "[s7590-pc] plant n=%d port=0x%x sem=0x%x\n", ++nplant, p, sm); fprintf(g_out, "PLANT n=%d t=%.0f\n", nplant, t);
      nextp += 30; }
  }
  return 0;
}
__attribute__((constructor)) static void s7590_init(void) {
  g_t0 = now(); const char *o = getenv("RS64_PC_OUT"); g_out = fopen(o ? o : "/tmp/rs64_portcensus.log", "w"); if (!g_out) g_out = stderr;
  pthread_t t; pthread_create(&t, 0, census_thr, 0); pthread_detach(t);
  g_ready = 1;
}
