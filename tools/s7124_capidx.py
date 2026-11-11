import sys,struct,os
# index a ROGUESQ_G5B_FRAME capture: swap mach hasram nranges bytes
f=open(sys.argv[1],'rb'); out=[]; cur=None
while True:
    t=f.read(4)
    if len(t)<4: break
    tag=struct.unpack('<I',t)[0]
    if tag==0x50415753:
        m,s=struct.unpack('<QI',f.read(12)); cur=[s,m,0,0,0]; out.append(cur)
    elif tag==0x204D4152: f.seek(0x1000000,1); cur[2]=1
    elif tag==0x20474E52:
        lo,n=struct.unpack('<II',f.read(8)); f.seek(n,1); cur[3]+=1; cur[4]+=n
    else: print('bad tag',hex(tag),f.tell(),file=sys.stderr); break
for r in out: print(*r)
