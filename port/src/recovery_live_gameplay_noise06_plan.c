#include "experimental_direct_paula.h"
int recovery_live_gameplay_plan(const dp_u8 *,dp_u8,DPVoice *);
/* Reached neutral-history extension only:06 = PAL118 cycles, long LFSR.
 * NESdev APU_Noise period table; append wave10, preserve all old modes.
 * Approximate2048sample loop. Unsupported states remain atomic rejections. */
int recovery_live_gameplay_noise06_plan(const dp_u8 *r,dp_u8 enable,DPVoice *o){
 dp_u8 copy[16];DPVoice v;unsigned i;
 if(r[14]!=6)return recovery_live_gameplay_plan(r,enable,o);
 for(i=0;i<16;i++)copy[i]=r[i];
 copy[14]=7;
 if(!recovery_live_gameplay_plan(copy,enable,&v))return 0;
 v.wave[3]=10;
 *o=v;return 1;
}
