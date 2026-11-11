#!/usr/bin/env python3
"""Mutations of the real stock-target capture, including configuration and pixels."""
import functools,json,struct,tempfile
from pathlib import Path
from PIL import Image
import verify_recovery_state_startup_display as v

def main():
 out=v.OUT;chip=(out/'chip.bin').read_bytes();rom=(v.PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();log=(out/'amiga.log').read_text()
 v.oracle=functools.lru_cache()(v.oracle);v.display.expected=functools.lru_cache()(v.display.expected)
 v.check(chip,rom,log);v.display.verify_screen(chip,out/'screen.ppm')
 p=chip.index(b'CDRSTA01');f=struct.unpack_from('>16I',chip,p+8)
 cases=[('startup marker',p)]+[(f'startup report {i}',p+8+4*i+3) for i in range(16)]
 for name,a,n in [('RAM',f[4],2048),('context',f[5],8),('journal',f[6],32770),('runtime',f[7],12),('resource',f[8],131072),('stack',f[9],4096),('captures',f[11],786432)]:
  cases += [(name+' lower guard',a-1),(name+' upper guard',a+n)]
  if name!='stack':cases += [(name+' content',a)]
 cases += [('stack scratch bound',f[9]+3071),('capture context',f[11]+4),('capture runtime',f[11]+12),('capture size',f[11]+27),('capture RAM size',f[11]+31)]
 p=chip.index(b'CDRDIS01');d=struct.unpack_from('>10I',chip,p+8)
 cases += [('display marker',p),('display status',p+11)]+[(f'display pointer {i}',p+8+4*i) for i in range(1,8)]
 cases += [(f'device {i}',d[1]+i) for i in range(28)]
 for name,a,n in [('NT',d[2],2048),('palette',d[3],32),('OAM',d[4],256),('CHR',d[5],8192),('frame',d[6],51200)]:
  cases += [(name+str(i),a+i) for i in (0,n//2,n-1)]
 cases += [(f'Copper header {i}',d[7]+i) for i in range(88)]
 cases += [(f'Copper color {i}',d[7]+88+4*i+3) for i in range(32)]
 rejected=[]
 for name,off in cases:
  bad=bytearray(chip);bad[off]^=1
  try:v.check(bytes(bad),rom,log)
  except (AssertionError,ValueError,struct.error):rejected.append(name)
  else:raise AssertionError('Accepted mutation: '+name)
 # Every individual bit of the four final Copper WAIT terminator bytes.
 for byte in range(4):
  for bit in range(8):
   bad=bytearray(chip);bad[d[7]+216+byte]^=1<<bit
   try:v.check(bytes(bad),rom,log)
   except AssertionError as error:
    assert str(error)=='Copper terminator',('Wrong rejection reason',byte,bit,error)
    rejected.append(f'Copper terminator byte {byte} bit {bit}')
   else:raise AssertionError(('Accepted Copper terminator corruption',byte,bit))
 for name,bad in [('truncated',chip[:-1]),('extended',chip+b'\0')]:
  try:v.check(bad,rom,log)
  except AssertionError:rejected.append(name)
  else:raise AssertionError(name)
 for field in ('cpu_model=68020','chipset=aga','fastmem_size=0','chipmem_size=4'):
  assert field in log
  try:v.check(chip,rom,log.replace(field,field+'INVALID'))
  except AssertionError:rejected.append('configuration '+field)
  else:raise AssertionError(field)
 with tempfile.TemporaryDirectory() as t:
  path=Path(t)/'bad.png';im=Image.open(out/'screen.ppm');im.putpixel((40,18),(255,0,0));im.save(path)
  try:v.display.verify_screen(chip,path)
  except AssertionError:rejected.append('actual viewport pixel')
  else:raise AssertionError('Pixel mutation accepted')
 result=dict(status='PASS',real_target_baseline=True,mutations_rejected=len(rejected),copper_terminator_single_bit_mutations_rejected=32,cases=rejected)
 (out/'rejection.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(rejected),'capture/configuration/video mutations rejected')
if __name__=='__main__':main()
