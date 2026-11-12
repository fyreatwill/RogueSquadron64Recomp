# s7189: per-swap (only on change) SETSCISSOR lr / colour-image width / FILLRECT lr from a ROGUESQ_G5B_FRAME capture. usage: s7189_cap_perswap.py CAP
import struct, sys, collections
cap=sys.argv[1]; f=open(cap,'rb'); s=-1; per=collections.defaultdict(lambda:[collections.Counter(),collections.Counter(),collections.Counter()])
while True:
    b=f.read(4)
    if len(b)<4: break
    t=struct.unpack('<I',b)[0]
    if t==0x50415753: m,s=struct.unpack('<QI',f.read(12))
    elif t==0x204D4152: f.seek(0x1000000,1)
    elif t==0x20474E52:
        l,n=struct.unpack('<II',f.read(8)); d=f.read(n); a=0
        while a+8<=len(d):
            w0,w1=struct.unpack_from('<II',d,a); op=(w0>>24)&0x3F; k=8
            if 8<=op<=15: k=32+(64 if op&4 else 0)+(64 if op&2 else 0)+(16 if op&1 else 0)
            elif op in(0x24,0x25): k=16
            elif op==0x2D: per[s][0][((w1>>12)&0xFFF)/4,(w1&0xFFF)/4]+=1
            elif op==0x3F: per[s][1][(w0&0x3FF)+1]+=1
            elif op==0x36: per[s][2][((w0>>12)&0xFFF)/4,(w0&0xFFF)/4]+=1
            a+=k
    else: print('bad',hex(t)); break
prev=None
for s in sorted(per):
    sc,ci,fr=per[s]; key=(tuple(sorted(sc)),tuple(sorted(ci)),tuple(sorted(fr))[:3])
    if key!=prev: print(s,'sc',sorted(sc)[:4],'ci',sorted(ci),'fill',sorted(fr)[:3]); prev=key
