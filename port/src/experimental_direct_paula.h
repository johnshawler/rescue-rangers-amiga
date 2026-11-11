/* Restricted, approximate frame-state adapter, not a general NES APU. */
#ifndef EXPERIMENTAL_DIRECT_PAULA_H
#define EXPERIMENTAL_DIRECT_PAULA_H
typedef unsigned char dp_u8;
typedef unsigned short dp_u16;
typedef unsigned long dp_u32;
typedef struct { dp_u16 period[4],volume[4],wave[4]; } DPVoice;
/* r: 4000..400F. enable:4015. Unsupported states reject atomically.
 * Caller supplies frame-final state; phase/length/linear envelopes not modeled.
 * Explicitly supports only halted constant pulse/noise and sweep08, tri00/FF.
 */
int experimental_direct_paula_plan(const dp_u8 *r,dp_u8 enable,DPVoice *out);
#endif
