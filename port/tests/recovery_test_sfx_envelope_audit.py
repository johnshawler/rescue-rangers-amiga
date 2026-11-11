"""Check static instruction annotations against original code, only with --rom."""
import hashlib,re,sys
from pathlib import Path
PORT=Path(__file__).resolve().parents[1]
source=(PORT/'src/recovery_sfx_envelope.s').read_text()
labels=re.findall(r'^\.p([0-9a-f]+): ; (.*)$',source,re.M)
assert len(labels)==343 and len({a for a,_ in labels})==343
refs=set(re.findall(r'\b(?:bsr|bra|bne|beq|bcs|bcc|bhi|bpl|bmi)\.\w+ \.p([0-9a-f]+)',source))
assert refs<={a for a,_ in labels}
if '--rom' in sys.argv:
 from py65.disassembler import Disassembler
 from py65.devices.mpu6502 import MPU
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
 assert hashlib.sha256(rom).hexdigest()=='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
 mem=[0]*65536;mem[0x8000:0xc000]=rom[49168:65552];d=Disassembler(MPU(memory=mem))
 def canon(s):return re.sub(r'\$([0-9a-f]+)',lambda m:'$'+format(int(m[1],16),'x'),s.lower().replace(' ',''))
 for pc,txt in labels:
  size,actual=d.instruction_at(int(pc,16))
  assert canon(actual)==canon(txt),(pc,txt,actual)
 print('PASS all 343 static instruction annotations match the original cartridge.')
else:print('PASS static instruction label uniqueness and reference closure; cartridge audit requires --rom.')
# Reachability uses the original control-flow annotations. Three branches are
# forced by X<4 or a preceding constant load; 880F cannot take the music arm.
code={int(pc,16):text for pc,text in labels};pcs=sorted(code)
next_pc=dict(zip(pcs,pcs[1:]));edges={}
for pc,text in code.items():
 op=text.split()[0];match=re.search(r'\$([0-9a-f]+)',text);dest=int(match[1],16) if match else None
 if pc==0x86bc:edges[pc]=[0x8023] # Dispatcher consumes this JSR frame.
 elif pc==0x8037:edges[pc]=[0x86c9,0x86de,0x8718,0x86fa,0x890d]
 elif pc in (0x871a,0x8737,0x8752):edges[pc]=[dest]
 elif pc==0x880f:edges[pc]=[next_pc[pc]]
 elif op=='RTS':edges[pc]=[]
 elif op=='JMP':edges[pc]=[dest]
 elif (op.startswith('B') and op!='BIT') or op=='JSR':edges[pc]=[dest,next_pc[pc]]
 else:edges[pc]=[next_pc[pc]]
reachable=set();pending=[0x86b2]
while pending:
 pc=pending.pop()
 if pc in reachable:continue
 reachable.add(pc);pending.extend(edges[pc])
assert len(reachable)==323
assert set(code)-reachable=={0x871c,0x871e,0x871f,0x8721,0x8724,0x8726,0x8728,0x872a,0x872c,0x872e,0x8739,0x873b,0x873d,0x873f,0x8742,0x8744,0x8747,0x8749,0x8754,0x8757}
if '--coverage-log' in sys.argv:
 log=Path(sys.argv[sys.argv.index('--coverage-log')+1]).read_text()
 actual={int(v,16) for v in re.search(r'Original instruction coverage: (.*)',log)[1].split(',')}
 assert actual==reachable,('missing',[hex(pc) for pc in sorted(reachable-actual)],'unexpected',[hex(pc) for pc in sorted(actual-reachable)])
 print('PASS original execution covered all 323 reachable instructions.')
else:print('PASS 323 reachable instructions; 20 music-only instructions excluded by the SFX contract.')
