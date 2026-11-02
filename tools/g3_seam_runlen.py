# s6798 companion to tools/g3_seam_intra.py: for every line the seam scorer flags, the longest CONTIGUOUS run (rows for a col, cols for a row) of seam pixels.
# A rasteriser seam is one long run; glyph strokes are many short ones.
# Usage: python3 tools/g3_seam_runlen.py <capture dir>   (same times.txt/arm filter as g3_seam_intra.py)
import sys,glob,os
src=open('tools/g3_seam_intra.py').read(); src=src[:src.index('def flatpatch')]
d=sys.argv[1]; sys.argv=[0,d]; exec(src)
import collections; H=collections.Counter(); worst=[]
for f in sorted(glob.glob(d+'/w*.png')):
    c=int(os.path.basename(f).split('_')[1])
    if c not in T: continue
    im=Image.open(f).convert('RGB'); s=seams(im)
    if not s: continue
    I=im.crop((4,TOP,im.size[0]-4,im.size[1]-4))
    ms={0:mask(I,3,0),1:mask(I,0,3)}
    for k,p in s:
        ax=0 if k=='col' else 1; m=ms[ax]; best=run=0
        if ax==0:
            x=p-4; it=(m.getpixel((x,y)) for y in range(m.size[1]))
        else:
            y=p-TOP; it=(m.getpixel((x,y)) for x in range(m.size[0]))
        for v in it:
            run=run+1 if v else 0; best=max(best,run)
        H[min(best//20*20,200)]+=1; worst.append((best,os.path.basename(f)[:4],k,p))
print('longest-run histogram (bin=20px):',sorted(H.items()))
print('top5',sorted(worst)[-5:])
