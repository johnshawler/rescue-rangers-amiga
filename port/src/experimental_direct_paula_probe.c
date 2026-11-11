#include "experimental_direct_paula.h"
#include "experimental_direct_paula_private.h"
static const signed char pulse[4][8] __attribute__((aligned(2)))={
 {-64,64,-64,-64,-64,-64,-64,-64}, {-64,64,64,-64,-64,-64,-64,-64},
 {-64,64,64,64,64,-64,-64,-64}, {64,-64,-64,64,64,64,64,64}};
static const signed char tri[32] __attribute__((aligned(2)))={60,52,44,36,28,20,12,4,-4,-12,-20,-28,-36,-44,-52,-60,-60,-52,-44,-36,-28,-20,-12,-4,4,12,20,28,36,44,52,60};
volatile struct {char magic[8];dp_u32 stage,frame,total,max_ticks,sum_ticks,rejects,updates,start,end;} dp_report={"DIRPAU01",0,0,DP_FRAMES,0,0,0,0,0,0};
static volatile dp_u16 *const hw=(volatile dp_u16*)0xdff000;
static dp_u16 oldwave[4]={65535,65535,65535,65535};
static dp_u32 tod(void){dp_u32 h=*(volatile dp_u8*)0xbfea01,m=*(volatile dp_u8*)0xbfe901,l=*(volatile dp_u8*)0xbfe801;return h*65536+m*256+l;}
static dp_u16 timer(void){dp_u16 h,l,h2;do{h=*(volatile dp_u8*)0xbfe501;l=*(volatile dp_u8*)0xbfe401;h2=*(volatile dp_u8*)0xbfe501;}while(h!=h2);return l+256*h;}
static void frame(void){hw[0x9c/2]=0x20;while(!(hw[0x1e/2]&0x20)){};}
static void apply(const DPVoice *v){unsigned i;for(i=0;i<4;i++){
 unsigned a=(0xa0+16*i)/2;dp_u16 w=v->wave[i];
 if(w!=oldwave[i]){const signed char *p=w<4?pulse[w]:w==4?tri:dp_noise[w-5];
 /* Change next DMA reload; no forced DMA reset. Transition latency is bounded
  * by current loop duration, including ~92ms noise loops. */
 hw[a]=(dp_u32)p>>16;hw[a+1]=(dp_u32)p;hw[a+2]=w<4?4:w==4?16:1024;oldwave[i]=w;}
 hw[a+3]=v->period[i];hw[a+4]=v->volume[i];}}
static void update(const dp_u8 *r){DPVoice v;dp_u16 a=timer(),dt;
 if(experimental_direct_paula_plan(r,15,&v))apply(&v);else dp_report.rejects++;
 dt=a-timer();dp_report.sum_ticks+=dt;if(dt>dp_report.max_ticks)dp_report.max_ticks=dt;dp_report.updates++;}
void experimental_direct_paula_main(void){unsigned i,j;dp_u8 r[16]={0x30,8,235,8,0x30,8,235,8,0,0,235,8,0x30,0,7,8};
 hw[0x9a/2]=0x7fff;hw[0x96/2]=0x7fff;hw[0x9c/2]=0x7fff;hw[0x9e/2]=0x7fff;hw[0x100/2]=0x200;
 *(volatile dp_u8*)0xbfee01=0;*(volatile dp_u8*)0xbfe401=255;*(volatile dp_u8*)0xbfe501=255;*(volatile dp_u8*)0xbfee01=17;
 update(r);hw[0x96/2]=0x820f;dp_report.stage=1;dp_report.start=tod();
 /* Synthetic blocks: pulse1,pulse2,triangle,noise07,noise0D,noise81,all,silence. */
 for(i=0;i<8;i++){r[0]=r[4]=r[12]=0x30;r[8]=0;
 if(i==0||i==6)r[0]=0xbf;if(i==1||i==6)r[4]=0xbf;if(i==2||i==6)r[8]=255;
 if(i>=3&&i<=6){r[12]=0x3f;r[14]=i==4?13:i==5?129:7;}
 update(r);for(j=0;j<50;j++)frame();}
 dp_report.stage=2;for(i=0;i<DP_FRAMES;i++){frame();update(dp_frames[i]);dp_report.frame=i+1;}
 dp_report.end=tod();dp_report.stage=3;for(i=0;i<4;i++)hw[(0xa8+16*i)/2]=0;
 for(;;){}
}
