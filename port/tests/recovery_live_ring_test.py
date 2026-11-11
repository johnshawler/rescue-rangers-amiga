#!/usr/bin/env python3
"""Compiled live adapter ring/limit regression; synthetic clock is not timing."""
from pathlib import Path
import sys
# Reuse the complete unchanged unit harness, adding checks in its initialized
# valid silent state before its existing rejection cases. Assert exact injection.
source=(Path(__file__).with_name('recovery_menu_paula_adapter_test.py')).read_text()
needle=' # Unsupported state at a completed RTI must fail and mute, never publish.'
assert source.count(needle)==1
checks='''
 # Execute4095 further real compiled publications, wrapping the telemetry ring.
 for ordinal in range(1,4096):
  assert call(4,0x80000,2,8)==1
  assert mem.r32(mp+16)==ordinal+1
  q=tr+56*(ordinal&255)
  assert mem.r16(q+12)==8 and mem.r16(q+14)==0
 assert mem.r32(mp+68)==0
 writes.clear();assert call(4,0x80000,2,8)==0
 assert mem.r32(mp+16)==4096 and mem.r32(mp+8)==99 and mem.r32(mp+68)==1
 assert any(a==0xdff096 and v==15 for a,w,v in writes)
 # Reset into the same valid state for unchanged rejection checks below.
 mem,call,writes=unit();journal(mem,ev)
 assert call(4,0x80000,2+4*len(ev),9)==1
 journal(mem,[]);assert call(4,0x80000,2,8)==1
'''
assert source.count('cpu.w_sr(0x2700)')==1
source=source.replace(needle,checks+needle).replace('cpu.w_sr(0x2700)','cpu.w_sr(0)')
exec(compile(source,__file__,'exec'))
