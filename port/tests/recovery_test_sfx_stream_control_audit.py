"""Static closure, optional original annotation and instruction coverage audit."""
import hashlib,re,sys,random
from pathlib import Path
PORT=Path(__file__).resolve().parents[1]
source=(PORT/'src/recovery_sfx_stream_control.s').read_text()
labels=re.findall(r'^\.p([0-9a-f]+): ; (.*)$',source,re.M)
assert len(labels)==55 and len({a for a,_ in labels})==55
refs=set(re.findall(r'\b(?:bsr|bra|bne|beq|bcs|bcc|bhi|bpl|bmi)\.\w+ \.p([0-9a-f]+)',source))
assert refs<={a for a,_ in labels}
assert '.resource:' not in source and '.adc:' not in source and '.sbc:' not in source
if '--rom' in sys.argv:
 from py65.disassembler import Disassembler
 from py65.devices.mpu6502 import MPU
 from recovery_test_startup_fade_continue import CPU
 from recovery_test_resident_pending_sfx27 import CompleteBus,SHA
 from recovery_test_sfx_stream_control import make_checker
 from recovery_sfx_stream_control_model import model
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 mem=[0]*65536;mem[0x8000:0xc000]=rom[49168:65552];d=Disassembler(MPU(memory=mem))
 for pc,txt in labels:assert d.instruction_at(int(pc,16))[1]==txt
 coverage=set();rng=random.Random(0x81b2)
 def reference(s,c,r):
  bus=CompleteBus(rom);bus.map_bank(3);bus[:2048]=s;bus.events.clear();ref=CPU(memory=bus);ref.pc=0x8235;ref.a,ref.x,ref.y,ref.p,ref.sp=c[2:7]
  for _ in range(300):
   at=ref.pc;coverage.add(at);ref.step()
   if at in (0x81b2,0x823c):break
  else:raise AssertionError('timeout')
  result=bytes(bus[:2048]),ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,c[7])),list(bus.events)
  assert result==model(s,c,r);return result
 check,cleanup=make_checker(reference)
 for mask in range(256):
  for branch in (0,1):
   s=bytearray(rng.randbytes(2048));s[0xcf]=mask;s[0xd7]=branch
   for i in range(4):
    if mask>>i&1:s[0x750+i]=s[0x754+i]=0
   c=bytes.fromhex('8235')+bytes((mask,mask,mask,mask,mask,0xa7));check(bytes(s),c,bytes(16384))
 cleanup();assert coverage=={int(pc,16) for pc,_ in labels},sorted(coverage^{int(pc,16) for pc,_ in labels})
 print('PASS 512 original/native/model cases; all 55 original instructions executed and audited')
else:print('PASS 55 unique static instructions, closed branches, no resource/arithmetic helper')
