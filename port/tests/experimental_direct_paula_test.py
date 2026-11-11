#!/usr/bin/env python3
"""Actual M68EC020 ABI and atomic rejection tests; no game resources."""
import json,os,random,struct,subprocess
from pathlib import Path
import machine68k
P=Path(__file__).resolve().parents[1];B=P/'build/experimental-direct-paula';B.mkdir(parents=True,exist_ok=True)
cc=os.environ.get('PAULA_CC','m68k-linux-gnu-gcc');elf=B/'unit.elf'
subprocess.run([cc,'-m68020','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fno-pie','-nostdlib','-Wl,-Ttext=0x1000','-Wl,-e,experimental_direct_paula_plan',str(P/'src/experimental_direct_paula.c'),'-o',str(elf)],check=True)
subprocess.run([cc.replace('gcc','objcopy'),'-O','binary','--only-section=.text',str(elf),str(B/'unit.bin')],check=True)
m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);mem,cpu=m.mem,m.cpu;mem.w_block(0x1000,(B/'unit.bin').read_bytes());mem.w16(0x800,0x60fe)
rng=random.Random(17);rejects=0;worst=0
for n in range(1600):
 r=[0x30,8,0,0,0x30,8,0,0,0,0,0,0,0x30,0,7,0];enable=rng.randrange(16)
 for base in (0,4,8):
  t=rng.randrange(2048);r[base+2]=t&255;r[base+3]=(t>>8)|8
  r[base]=rng.randrange(4)*64+48+rng.randrange(16) if base<8 else rng.choice([0,255])
 r[12]=48+rng.randrange(16);r[14]=rng.choice([7,13,129])
 if n%4==0:r[rng.choice([0,1,4,5,8,12,14])]=rng.randrange(256)
 if n%19==0:enable|=16
 periods=[];volumes=[];waves=[]
 valid=not enable&~15 and r[1]==r[5]==8 and r[8] in (0,255) and all(r[x]&48==48 for x in (0,4,12)) and r[14] in (7,13,129)
 for i,base in enumerate((0,4,8)):
  t=r[base+2]+((r[base+3]&7)<<8);period=round(3546895/1662607*(t+1)*(2 if i<2 else 1))
  volume=(2*(r[base]&15) if i<2 else 24) if enable&(1<<i) and t>=(8 if i<2 else 2) and (i<2 or r[8]) else 0
  if period<124:
   if volume:valid=False
   period=124
  periods.append(period);volumes.append(volume);waves.append(r[base]>>6 if i<2 else 4)
 periods.append(160);volumes.append(2*(r[12]&15) if enable&8 else 0);waves.append({7:5,13:6,129:7}.get(r[14],0))
 mem.w_block(0x10000,bytes(r));mem.w_block(0x20000,b'G'*16+b'X'*24+b'H'*16)
 sp=0x1f0000;cpu.w_sr(0x2700);cpu.w_sp(sp);mem.w32(sp,0x800)
 for i,a in enumerate([0x10000,enable,0x20010]):mem.w32(sp+4+4*i,a)
 saved={x:0x51000000+x for x in list(range(2,8))+list(range(10,15))}
 for reg,v in saved.items():cpu.w_reg(reg,v)
 cpu.w_pc(0x1000)
 for _ in range(100):
  cpu.execute(1000)
  if cpu.r_pc()==0x800:break
 else:raise AssertionError('timeout')
 assert cpu.r_sp()==sp+4 and all(cpu.r_reg(k)==v for k,v in saved.items())
 assert cpu.r_reg(0)==bool(valid),(n,r,enable)
 assert bytes(mem.r_block(0x10000,16))==bytes(r)
 actual=bytes(mem.r_block(0x20010,24))
 if valid:assert actual==struct.pack('>12H',*(periods+volumes+waves))
 else:rejects+=1;assert actual==b'X'*24
 assert bytes(mem.r_block(0x20000,16))==b'G'*16 and bytes(mem.r_block(0x20028,16))==b'H'*16
result={'status':'PASS','native_calls':1600,'atomic_rejections':rejects,'ABI':'M68EC020 stack, callee saved registers, input/output bounds','timing':'Host functional execution only; not a target benchmark'}
(B/'unit.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
# Independent offline noise oracle: construct every CPU-cycle value, then
# integrate its prefix sum at rational Paula sample boundaries. This does not
# share the generator's event-countdown algorithm.
import importlib.util,math
spec=importlib.util.spec_from_file_location('direct_builder',P/'tools/experimental_direct_paula_build.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
for period,short in [(148,False),(944,False),(8,True)]:
 n=2048;state=1;prefix=[0]
 for cycle in range(math.ceil(n*160*1662607/3546895)+1):
  prefix.append(prefix[-1]+(-64 if state&1 else 64))
  if (cycle+1)%period==0:state=state//2+(((state&1)^((state>>(6 if short else 1))&1))*16384)
 def area(t):
  c,rem=divmod(t,3546895);return prefix[c]*3546895+rem*(prefix[c+1]-prefix[c])
 width=160*1662607
 oracle=[round((area((i+1)*width)-area(i*width))/width) for i in range(n)]
 assert oracle==builder.noise(period,short,n)
result['noise_box_integrated_bytes_independently_matched']=6144
(B/'unit.json').write_text(json.dumps(result,indent=2)+'\n');print('Independent noise oracle: PASS, 6144 bytes')
