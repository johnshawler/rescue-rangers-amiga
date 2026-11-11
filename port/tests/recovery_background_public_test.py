#!/usr/bin/env python3
"""Synthetic actual-68020 proof using the frozen independent pixel oracle.
No cartridge or target timing input. Both user and supervisor execution checked.
"""
from pathlib import Path
import hashlib
P=Path(__file__).resolve().parents[1]
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a))
 return s.replace(a,b,1)
def main():
 path=P/'tests/test_native_background.py';s=path.read_text()
 assert hashlib.sha256(path.read_bytes()).hexdigest()=='7e6ed0f74bccc9dbf2c8628c6366c3487aace3ae347732bbe42e2aaee86b76f2'
 # Read-only reuse keeps the independently written per-pixel reference unchanged.
 for source in ('native_background.s','recovery_background_single_read.s'):
  for seed in (68020,1,0xabcdef):
   for sr in (0x2700,0):
    code=once(s,"ROOT/'port/src/native_background.s'",f"ROOT/'port/src/{source}'")
    code=once(code,'random.Random(68020)',f'random.Random({seed})')
    code=once(code,'cpu.w_sr(0x2700)',f'cpu.w_sr({sr})')
    code=once(code,'mem.w16(0x800,0x60fe)',"mem.w_block(0xf0000-76,bytes([0xa5]*16));mem.w_block(0xf0004,bytes([0xa5]*16));mem.w16(0x800,0x60fe)")
    code=once(code,"assert cpu.r_sp()==0xf0004,name+': stack preservation'","assert cpu.r_sp()==0xf0004,name+': stack preservation'\n        assert bytes(mem.r_block(0xf0000-76,16))==bytes([0xa5]*16),name+': stack lower guard'\n        assert bytes(mem.r_block(0xf0004,16))==bytes([0xa5]*16),name+': stack upper guard'\n        assert bytes(mem.r_block(0x1000,len(code)))==code,name+': code modified'")
    code=once(code,'for _ in range(20000):',"accesses=[]\n        def trace(mode,width,addr,value):\n            assert mode in ('R','W') and width in (0,1,2)\n            accesses.append((mode,1<<width,addr))\n        mem.set_trace_func(trace);mem.set_trace_mode(True)\n        for _ in range(20000):")
    code=once(code,'for addr,length,want,kind in',"""mem.set_trace_mode(False)
        writable=((0xf0000-60,0xf0000),(0x10000,0x10000+51200),(0x20000,0x20000+7680),(0x22000,0x22000+1920))
        readable=writable+((0xf0000,0xf0004),(0x800,0x802),(0x1000,0x1000+len(code)),(0x2000,0x2400),(0x3000,0x4000))
        for mode,width,addr in accesses:
            allowed=writable if mode=='W' else readable
            assert any(lo<=addr and addr+width<=hi for lo,hi in allowed),(name,mode,width,hex(addr),'access outside ABI regions')
            if mode=='W' and expected[3]==0:assert 0xf0000-60<=addr and addr+width<=0xf0000,name+': unchanged tile wrote output'
        for addr,length,want,kind in""")
    print(source,'seed',seed,'SR',sr)
    ns={'__file__':str(path),'__name__':'frozen_background_oracle'}
    exec(compile(code,str(path),'exec'),ns);ns['main']()
 print('PASS 84 assembled cases; width-aware read/write bounds, immutable code/NT/CHR, 60-byte stack guards. No timing claim.')
if __name__=='__main__':main()
