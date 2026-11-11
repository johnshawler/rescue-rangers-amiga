#include "experimental_direct_paula.h"
int recovery_stage_target_plan(const dp_u8 *,dp_u8,DPVoice *);
/* Bounded extension only: $8E is PAL1890 cycles, short (bit0 XOR bit6).
 * Source: https://www.nesdev.org/wiki/APU_Noise (period table and mode bit).
 * Wave9 is an approximate2048sample loop, not phase-accurate NES synthesis.
 * All predecessor modes/guards remain exact. Reject without publishing output. */
int recovery_live_gameplay_plan(const dp_u8 *r,dp_u8 enable,DPVoice *o){
 dp_u8 copy[16];DPVoice v;unsigned i;
 if(r[14]!=0x8e)return recovery_stage_target_plan(r,enable,o);
 for(i=0;i<16;i++)copy[i]=r[i];
 copy[14]=7;
 if(!recovery_stage_target_plan(copy,enable,&v))return 0;
 v.wave[3]=9;
 *o=v;return 1;
}
