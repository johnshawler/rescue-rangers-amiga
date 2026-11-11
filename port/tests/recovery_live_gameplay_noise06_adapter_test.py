#!/usr/bin/env python3
"""ROM-free compiled stage-adapter ABI and long-journal sentinel checks."""
from pathlib import Path
source=Path(__file__).with_name('recovery_menu_paula_adapter_test.py').read_text()
needle=' # Unsupported state at a completed RTI must fail and mute, never publish.'
assert source.count(needle)==1
source=source.replace(needle,''' # Both genuine long NMI producers admit the FFFF size sentinel.
 for helper in (48,98):
  journal(mem,[]);before=mem.r32(mp+16)
  assert call(4,0x80000,65535,helper)==1
  assert mem.r32(mp+16)==before
 # Genuine stage08 selects the appended PAL188 long-mode DMA buffer.
 journal(mem,[(0x400e,8),(0x400c,0x3b),(0x4015,8)])
 assert call(4,0x80000,14,134)==1
 journal(mem,[]);assert call(4,0x80000,2,42)==1
 q=mem.r32(mp+48)+56
 assert mem.r16(q+54)==8
 ptr=(mem.r16(0xdff0d0)<<16)|mem.r16(0xdff0d2)
 assert ptr==0x1000+symbols['dp_noise']+3*2048
 assert mem.r16(0xdff0d4)==1024 and mem.r16(0xdff0d6)==160 and mem.r16(0xdff0d8)==22
 # New8E selects only the fifth finite loop, after ordered counted writes.
 journal(mem,[(0x400e,0x8e),(0x400c,0x3b),(0x4015,8)])
 assert call(4,0x80000,14,134)==1
 journal(mem,[]);assert call(4,0x80000,2,42)==1
 q=mem.r32(mp+48)+112
 assert mem.r16(q+54)==9
 ptr=(mem.r16(0xdff0d0)<<16)|mem.r16(0xdff0d2)
 assert ptr==0x1000+symbols['dp_noise']+4*2048
 assert mem.r16(0xdff0d4)==1024 and mem.r16(0xdff0d6)==160 and mem.r16(0xdff0d8)==22
 # Reached neutral06 selects appended long-mode PAL118 loop only.
 journal(mem,[(0x400e,6),(0x400c,0x3e),(0x4015,8)])
 assert call(4,0x80000,14,134)==1
 journal(mem,[]);assert call(4,0x80000,2,42)==1
 q=mem.r32(mp+48)+168
 assert mem.r16(q+54)==10
 ptr=(mem.r16(0xdff0d0)<<16)|mem.r16(0xdff0d2)
 assert ptr==0x1000+symbols['dp_noise']+5*2048
 assert mem.r16(0xdff0d4)==1024 and mem.r16(0xdff0d6)==160 and mem.r16(0xdff0d8)==28
 # New region size admits exactly the 15000-record bound, not one more.
 mem.w_block(0x80000,bytes.fromhex('3a98')+bytes.fromhex('80000000')*15000)
 assert call(4,0x80000,60002,134)==1
 mem,call,writes=unit();mem.w16(0x80000,15001)
 assert call(4,0x80000,60002,134)==0 and mem.r32(mp+8)==99
 mem,call,writes=unit();journal(mem,ev)
 assert call(4,0x80000,2+4*len(ev),9)==1
 journal(mem,[]);assert call(4,0x80000,2,8)==1
'''+needle).replace('cpu.w_sr(0x2700)','cpu.w_sr(0)')
exec(compile(source,__file__,'exec'))
