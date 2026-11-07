// s6920: 16-frame gap across each toggle vs the same gap inside one state (before and after): the second is the same-run control for camera motion. Pair-minus-control per toggle, band rows h/6..h/2 and whole. usage: span file [G=8] [skip s]
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <vector>
#include <algorithm>
using namespace std;
int main(int c,char**a){ FILE*f=fopen(a[1],"rb"); int G=c>2?atoi(a[2]):8; int V=c>3?atoi(a[3]):0; uint64_t t; uint32_t w,h; fread(&t,8,1,f);fread(&w,4,1,f);fread(&h,4,1,f); size_t n=(size_t)w*h*3,fs=16+n; fseeko(f,0,SEEK_END); size_t N=ftello(f)/fs; vector<uint64_t> T(N);
 for(size_t i=0;i<N;i++){fseeko(f,i*fs,SEEK_SET);fread(&T[i],8,1,f);}
 auto get=[&](size_t i,vector<uint8_t>&b){fseeko(f,i*fs+16,SEEK_SET);fread(b.data(),1,n,f); if(V&&((T[i]/24000000)&1)) for(size_t k=h/6*w*3;k<h/2*w*3;k++){int x=b[k]+V;b[k]=x>255?255:x;}};
 vector<uint8_t> A(n),B(n),C(n),D(n); auto mad=[&](vector<uint8_t>&x,vector<uint8_t>&y){double s=0;size_t y0=h/6*w*3,y1=h/2*w*3;for(size_t i=y0;i<y1;i++)s+=abs((int)x[i]-y[i]);return s/(y1-y0);};
 struct R{double ac,wi;size_t i;int to;}; vector<R> r;
 for(size_t i=1;i<N;i++) if(((T[i]/24000000)&1)!=((T[i-1]/24000000)&1)){ if(i<3*G+1||i+3*G+1>=N)continue; get(i-G,A);get(i+G,B);get(i-3*G,C);get(i+3*G,D); r.push_back({mad(A,B),(mad(C,A)+mad(B,D))/2,i,(int)((T[i]/24000000)&1)}); }
 vector<double> d; int pos=0; for(auto&x:r){d.push_back(x.ac-x.wi);pos+=x.ac>x.wi;} sort(d.begin(),d.end()); double m=0; for(double v:d)m+=v; m/=d.size();
 printf("%s toggles %zu across-minus-within band: mean %.3f p50 %.3f p10 %.3f p90 %.3f, across>within %d\n",a[1],d.size(),m,d[d.size()/2],d[d.size()/10],d[d.size()*9/10],pos);
 sort(r.begin(),r.end(),[](const R&x,const R&y){return x.wi<y.wi;}); { size_t q=r.size()/4; vector<double> e; int p=0; for(size_t i=0;i<q;i++){e.push_back(r[i].ac-r[i].wi);p+=r[i].ac>r[i].wi;} sort(e.begin(),e.end()); printf(" quiet quarter n %zu across-within p50 %.3f, across>within %d, within max %.2f\n",q,e[q/2],p,r[q-1].wi);} printf(" quietest toggles (frame, to, across, within):"); for(size_t i=0;i<8&&i<r.size();i++)printf(" %zu/%s/%.2f/%.2f",r[i].i,r[i].to?"live":"lat",r[i].ac,r[i].wi); puts("");
}
