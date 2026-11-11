"""Public declarative helper contracts. No cartridge, original CPU or private imports."""
from importlib import import_module
NAMES = ('character_cursor_sound_request','pending_sfx27_dispatch','sfx_header_initialize','sfx_initialized_tail','sfx_stream_entry','sfx_duration_math','sfx_channel_reconfigure','sfx_phase_dispatch','sfx_tick_entry','sfx_command_mask','sfx_event_action','sfx_active_control','sfx_envelope','sfx_stream_control')
MODELS={56+i:import_module('recovery_test_'+name).model for i,name in enumerate(NAMES)}
def preflight(index,s,c,r):
 if index==57:return [0xa00]
 if index in (65,68):return import_module('recovery_test_'+NAMES[index-56]).validation_reads(s,c,r)
 return []

from recovery_test_pending_sfx27_dispatch import dequeue
MODELS[70]=dequeue

def tail(s,c,r):
 sp=c[6];x=s[0xdb]
 if c[:2]!=bytes.fromhex('8151') or x>=8 or s[0xdc+x]!=136:return None
 if bytes(s[256+((sp+i)&255)] for i in range(1,5))!=bytes.fromhex('e580f2c0'):return None
 state=bytearray(s);state[0xc0]=(s[0xc0]-1)&255
 context=bytes.fromhex('c0f6')+bytes((136,x,c[4],(c[5]&0x7c)|3,(sp+4)&255,c[7]))
 return bytes(state),context,[('ram',0xc0,state[0xc0])]
MODELS[71]=tail
