import sys,glob,os
from PIL import Image, ImageChops, ImageDraw
# s6797: intra-frame seam detector split by ROGUESQ_EXACT_EDGES=tog arm (on = odd epoch second, times.txt
# "<n> <t0> <t1>", capture kept only inside one second >=0.15 s past the boundary). A seam = a 1-2 window-px
# column/row whose pixels differ by >40 (max channel) from the pixels 3 px either side while those two agree within 12
# (flat surround), over >=40 rows/cols. Window title bar (top 64 px) excluded. The cross-frame pair diff
# (tools/g3_edge_tog_pairs.py) is confounded by animated menus (pulsing text, spinning emblem), this is not.
# Positive control: a 2 px line drawn into a flat patch of every kept frame must be flagged.
# Usage: python3 tools/g3_seam_intra.py <capture dir>
d=sys.argv[1]; TOP=64
T={}
for l in open(d+'/times.txt'):
    c,a,b=l.split(); a=float(a.replace(',','.')); b=float(b.replace(',','.'))
    if int(a)==int(b) and a-int(a)>=0.15: T[int(c)]=int(a)&1
def mx(im):
    r,g,b=im.split(); return ImageChops.lighter(ImageChops.lighter(r,g),b)
def thr(im,t,hi): return im.point(lambda v:255 if (v>t if hi else v<=t) else 0)
def mask(I,dx,dy):
    L=ImageChops.offset(I,dx,dy); R=ImageChops.offset(I,-dx,-dy)
    a=thr(mx(ImageChops.difference(I,L)),40,1); b=thr(mx(ImageChops.difference(I,R)),40,1); c=thr(mx(ImageChops.difference(L,R)),12,0)
    return ImageChops.multiply(ImageChops.multiply(a,b),c)
def seams(im):
    I=im.crop((4,TOP,im.size[0]-4,im.size[1]-4)); w,h=I.size; out=[]
    for ax,(dx,dy) in ((0,(3,0)),(1,(0,3))):
        m=mask(I,dx,dy)
        sz=(w,1) if ax==0 else (1,h); n=h if ax==0 else w
        cnt=[v*n/255 for v in m.resize(sz,Image.BOX).get_flattened_data()]
        i=4
        while i<len(cnt)-4:
            if cnt[i]>=40:
                j=i
                while j<len(cnt) and cnt[j]>=40: j+=1
                if j-i<=2: out.append(('col' if ax==0 else 'row',i+(4 if ax==0 else TOP)))
                i=j
            else: i+=1
    return out
def flatpatch(im):
    g=mx(im)
    for y in range(TOP+100,im.size[1]-250,40):
        for x in range(100,im.size[0]-100,40):
            box=(x-8,y,x+8,y+200); e=g.crop(box).getextrema()
            if e[1]-e[0]<8: return x,y
    return None
st={0:[0,0,0,{}],1:[0,0,0,{}]}; pc=[0,0]
for f in sorted(glob.glob(d+'/w*.png')):
    c=int(os.path.basename(f).split('_')[1])
    if c not in T: continue
    im=Image.open(f).convert('RGB'); s=seams(im); a=T[c]; r=st[a]; r[0]+=1; r[1]+=len(s); r[2]+=bool(s)
    for k in s: r[3].setdefault(k,[]).append(os.path.basename(f)[:4])
    p=flatpatch(im)
    if p:
        x,y=p; C=im.copy(); v=C.getpixel((x,y)); nv=tuple(255 if q<128 else 0 for q in v)
        ImageDraw.Draw(C).rectangle((x,y,x+1,y+150),fill=nv); pc[0]+=1; pc[1]+=len(seams(C))>len(s)
for a in (0,1):
    r=st[a]; print('arm on=%d frames %d with-seam %d seams %d'%(a,r[0],r[2],r[1]))
    for k,v in sorted(r[3].items(),key=lambda kv:-len(kv[1]))[:10]: print('   %s %d frames %s'%(k,len(v),' '.join(v[:6])))
print('positive control: synthetic 2px line flagged %d/%d'%(pc[1],pc[0]))
