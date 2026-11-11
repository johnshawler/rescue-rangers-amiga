#include "experimental_direct_paula.h"
/* PAL ratio approximated by32/15; nominal integer clocks differ <0.1ppm.
 * No floating-point or per-sample work on the target. */
int experimental_direct_paula_plan(const dp_u8 *r,dp_u8 enable,DPVoice *o){
 DPVoice v; unsigned i,t;
 if(enable&~15 || r[1]!=8 || r[5]!=8 || (r[8]!=0 && r[8]!=255))return 0;
 if((r[0]&48)!=48 || (r[4]&48)!=48 || (r[12]&48)!=48)return 0;
 if(r[14]!=7 && r[14]!=13 && r[14]!=129)return 0;
 for(i=0;i<2;i++){t=r[4*i+2]+((r[4*i+3]&7)<<8);
  v.period[i]=(64*(t+1)+7)/15;v.wave[i]=r[4*i]>>6;
  v.volume[i]=(enable&(1<<i))&&t>=8?2*(r[4*i]&15):0;
 }
 t=r[10]+((r[11]&7)<<8);v.period[2]=(32*(t+1)+7)/15;
 v.volume[2]=(enable&4)&&r[8]&&t>=2?24:0;v.wave[2]=4;
 v.period[3]=160;v.volume[3]=(enable&8)?2*(r[12]&15):0;
 v.wave[3]=r[14]==7?5:r[14]==13?6:7;
 /* Muted out-of-range states use a safe period; audible ones reject. */
 for(i=0;i<4;i++)if(v.period[i]<124){if(v.volume[i])return 0;v.period[i]=124;}
 *o=v;return 1;
}
