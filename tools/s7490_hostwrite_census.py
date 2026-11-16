#!/usr/bin/env python3
"""s7490 class EO census: guest-memory accesses made by HOST code that bypass the generated RS64_S5798_ST / RS64_S7484_LD hooks.

Part A (decisive, from the linked binary's debug map): every generated RECOMP_FUNC game body that a strong definition from another
object overrides (RECOMP_FUNC is weak on clang). The generated body - and its hooks - is dead; the overrider must carry its own.
  zmemcpy -> upstream_compat.cpp (s7490 per-byte hook: fn=zmemcpy_host); PatchesLib bodies -> RS64_S7490_PST/PLD (fixup_patches_host.py).
Part B (inventory): host-implemented guest-called functions (calls in RecompiledFuncs with no generated definition) that store through
a guest pointer argument, with the s7486/s7489 host-access kind if one covers them.
Exit 0 = every Part A overrider that touches guest memory is hooked. Usage: s7490_hostwrite_census.py [binary] [--rows]"""
import re, glob, subprocess, sys, collections, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RF = os.path.join(ROOT, '..', 'N64Recomp', 'RecompiledFuncs')
BIN = next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(ROOT, 'build', 'RogueSquadron64Recomp'))
defs, calls = set(), collections.Counter()
for f in glob.glob(os.path.join(RF, '*.c')):
    s = open(f, errors='ignore').read()
    defs.update(re.findall(r'^(?:__attribute__\(\(weak\)\) )?RECOMP_FUNC void (\w+)\(uint8_t\* rdram', s, re.M))
    calls.update(re.findall(r'\b(\w+)\(rdram, ctx\)', s))
out = subprocess.run(['nm', '-a', '-p', BIN], capture_output=True, text=True).stdout
oso, owner = None, {}
for ln in out.splitlines():
    if ' OSO ' in ln: oso = ln.split(' OSO ')[-1].strip()
    elif ' FUN ' in ln:
        n = ln.split()[-1]
        if n.startswith('_') and n[1:] not in owner: owner[n[1:]] = oso
if not owner: sys.exit('no debug map in ' + BIN)
pc = open(os.path.join(ROOT, 'RecompiledPatches', 'patches.c'), errors='ignore').read()
uc = open(os.path.join(ROOT, 'src', 'main', 'upstream_compat.cpp'), errors='ignore').read()
def body(src, name):
    m = re.search(r'^(?:extern "C" )?(?:RECOMP_FUNC )?void ' + name + r'\(uint8_t\* rdram, recomp_context\* ctx\) \{', src, re.M)
    if not m: return ''
    e = src.find('\n}\n', m.end()); return src[m.start():e]
bad = 0; print('PART A: generated bodies overridden at link time')
for n in sorted(defs):
    o = owner.get(n)
    if not o or 'funcs' in o.split('/')[-1]: continue
    obj = o.split('/')[-1]
    if n == 'main': print(f'  {n:34s} {obj:32s} host entry, not a game body'); continue
    if 'patches.c' in obj:
        b = body(pc, n); inner = re.findall(r'static void (rs64_\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{', b)
        st = len(re.findall(r'^\s*MEM_[WHB]\(-?0X[0-9A-F]+, ctx->r\d+\) = ', pc[pc.find('RECOMP_FUNC void ' + n + '('):pc.find('\n}\n', pc.find('RECOMP_FUNC void ' + n + '('))], re.M))
        seg = pc[pc.find('RECOMP_FUNC void ' + n + '('):pc.find('\n}\n', pc.find('RECOMP_FUNC void ' + n + '('))]
        for h in sorted(set(re.findall(r'\b(rs64_\w+_body)\(rdram, ctx\)', seg))):  # fixup wrappers delegate to the generated body
            i = pc.find('static void ' + h + '(uint8_t* rdram, recomp_context* ctx) {')
            if i >= 0: seg += pc[i:pc.find('\n}\n', i)]
        acc = len(re.findall(r'MEM_[WHB]U?\(', seg)); hk = len(re.findall(r'RS64_S7490_P(ST|LD)\(0x', seg))
        ok = hk > 0 or acc == 0; bad += not ok
        print(f'  {n:34s} {obj:32s} callers={calls[n]:3d} mem_access={acc:3d} hooks={hk:3d} {"HOOKED" if ok else "BLIND"}')
    else:
        b = body(uc, n); w = len(re.findall(r'MEM_[WHB]\([^;]*\) = ', b)); hk = 's7490_marked' in b
        ok = hk or w == 0; bad += not ok
        print(f'  {n:34s} {obj:32s} callers={calls[n]:3d} host_stores={w} {"HOOKED (s7490)" if ok else "BLIND"}')
print('PART B: host-implemented guest calls that store through a guest pointer (inventory; kind = s7486/s7489 coverage)')
B = [('osRecvMesg_recomp', 'ultramodern mesgqueue.cpp do_recv: *msg_ out + mq->first/validCount', 'none'),
     ('osSendMesg_recomp', 'do_send: mq->msg[slot] + validCount', 'none'), ('osJamMesg_recomp', 'do_send jam: mq->msg[first]', 'none'),
     ('osCreateMesgQueue_recomp', 'mq fields', 'none'), ('osCreateThread_recomp', 'OSThread fields (threads.cpp)', 'none'),
     ('osContGetReadData_recomp', 'cont.cpp pad[6*n] button/stick/err', 'none'), ('osContInit_recomp', 'cont.cpp bitpattern byte + status', 'none'),
     ('osContGetQuery_recomp', 'cont.cpp status', 'none'), ('osEepromLongRead_recomp', 'pi.cpp save_read MEM_B loop', 'none'),
     ('osPiStartDma_recomp', 'pi.cpp:722 IoMesg fields + do_rom_read', 'pi_dma (data only)'), ('osDpGetCounters_recomp', 'upstream_compat 8 words', 'none'),
     ('osPfsReadWriteFile_recomp', 'pak.cpp buffer', 'none'),
     # s7492 class EQ: ultramodern thread-queue link stores (threadqueue.cpp insert/pop/remove) reached from these OS calls;
     # osPfsNumFiles (pak.cpp, the only pak.cpp body that stores) has 0 game callers; RT64 copyNativeToRAM -> os_rt64fb (main.cpp).
     ('osStartThread_recomp', 'threadqueue.cpp insert/pop: OSThread next/queue + queue head', 'none'),
     ('osSetThreadPri_recomp', 'threadqueue.cpp remove+insert', 'none'), ('osStopThread_recomp', 'threadqueue.cpp remove', 'none'),
     ('osPfsNumFiles_recomp', 'pak.cpp *max_files/*files_used (s32 via _arg TO_PTR: correct guest pointer)', 'none')]
# s7491 class EP: Part B sites now call RS64_S7491(a, w, "<kind>") after their stores (lib/ ultramodern + librecomp, upstream_compat
# osDpGetCounters). A function is covered when every kind it needs appears as a call in the sources; osPfsReadWriteFile stores nothing.
NEED = {'osRecvMesg_recomp': ['os_recv', 'os_recv_out'], 'osSendMesg_recomp': ['os_send'], 'osJamMesg_recomp': ['os_jam'],
        'osCreateMesgQueue_recomp': ['os_createmq'], 'osCreateThread_recomp': ['os_createthread'], 'osContGetReadData_recomp': ['os_contread'],
        'osContInit_recomp': ['os_continit'], 'osContGetQuery_recomp': ['os_contquery'], 'osEepromLongRead_recomp': ['os_saveread'],
        'osPiStartDma_recomp': ['os_iomesg'], 'osDpGetCounters_recomp': ['os_dpcounters'], 'osPfsReadWriteFile_recomp': [],
        'osStartThread_recomp': ['os_tq_link', 'os_tq_head'], 'osSetThreadPri_recomp': ['os_tq_link', 'os_tq_head'],
        'osStopThread_recomp': ['os_tq_head'], 'osPfsNumFiles_recomp': []}
LIB = os.path.join(ROOT, 'lib', 'N64ModernRuntime')
src = ''.join(open(f, errors='ignore').read() for f in glob.glob(os.path.join(LIB, 'ultramodern', 'src', '*.cpp')) + glob.glob(os.path.join(LIB, 'librecomp', 'src', '*.cpp'))) + uc
have = set(re.findall(r'RS64_S7491\([^;]*"(os_\w+)"\)', src)) | set(re.findall(r'rs64_s7491_hst\([^;]*"(os_\w+)"\)', src)) \
    | set(re.findall(r's7492_tq\([^;]*"(os_\w+)"\)', src))
bblind = 0
for n, what, k in B:
    need = NEED.get(n, ['?']); cov = all(x in have for x in need); bblind += not cov
    tag = 'no store (returns PFS_ERR_NOPACK)' if not need else ('s7491 ' + '/'.join(need) if cov else 'BLIND')
    print(f'  {n:28s} callers={calls[n]:3d}  {what:55s} kind={k} ep={tag}')
print(f'census: part_a_blind={bad} part_b_blind={bblind}'); sys.exit(1 if bad or bblind else 0)
