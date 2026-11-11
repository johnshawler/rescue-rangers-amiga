#include "experimental_direct_paula.h"
/* Additive bounded stage0 noise08 support. The title planner stays unchanged.
 * 08 selects PAL noise period188, long LFSR mode, synthetic2048sample loop.
 * Wave8 is appended after unchanged wave5/6/7. All other title guards apply.
 * No output is published on rejection; no input register is modified. */
int recovery_stage_target_plan(const dp_u8 *r,dp_u8 enable,DPVoice *o){
 dp_u8 copy[16];DPVoice v;unsigned i;
 if(r[14]!=8)return experimental_direct_paula_plan(r,enable,o);
 for(i=0;i<16;i++)copy[i]=r[i];
 copy[14]=7;
 if(!experimental_direct_paula_plan(copy,enable,&v))return 0;
 v.wave[3]=8;
 *o=v;return 1;
}
