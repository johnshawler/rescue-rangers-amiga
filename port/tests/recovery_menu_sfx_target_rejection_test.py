#!/usr/bin/env python3
"""Mutations of the real stock-target capture, including configuration and pixels."""
import functools,json,struct,tempfile
from pathlib import Path
from PIL import Image
import verify_recovery_menu_sfx_target as v

def main():
 out=v.OUT/'right_hold';chip=(out/'chip.bin').read_bytes();rom=(v.PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();log=(out/'amiga.log').read_text()
 v.oracle=functools.lru_cache()(v.oracle);v.display.expected=functools.lru_cache()(v.display.expected)
 v.check(chip,rom,log,'right_hold');v.display.verify_screen(chip,out/'screen.ppm')
 p=chip.index(b'CDRSFX01');f=struct.unpack_from('>21I',chip,p+8)
 cases=[('startup marker',p)]+[(f'startup report {i}',p+8+4*i+3) for i in range(21)]
 for name,a,n in [('RAM',f[4],2048),('context',f[5],8),('journal',f[6],134638),('runtime',f[7],12),('resource',f[8],131072),('stack',f[9],4096),('capture',f[16],262144)]:
  cases += [(name+' lower guard',a-1),(name+' upper guard',a+n)]
  if name not in ('stack','journal'):cases += [(name+' content',a)]
 cases += [('immutable native code',chip.index((out/'recovery_menu_sfx_target.bin').read_bytes()[:64])+10),('stack scratch bound',f[9]+3071),('last captured journal record',f[16]+f[17]-1),('capture unused tail',f[16]+f[17])]
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
  try:v.check(bytes(bad),rom,log,'right_hold')
  except (AssertionError,ValueError,struct.error):rejected.append(name)
  else:raise AssertionError('Accepted mutation: '+name)
 # Every individual bit of the four final Copper WAIT terminator bytes.
 for byte in range(4):
  for bit in range(8):
   bad=bytearray(chip);bad[d[7]+216+byte]^=1<<bit
   try:v.check(bytes(bad),rom,log,'right_hold')
   except AssertionError as error:
    assert str(error)=='Copper terminator',('Wrong rejection reason',byte,bit,error)
    rejected.append(f'Copper terminator byte {byte} bit {bit}')
   else:raise AssertionError(('Accepted Copper terminator corruption',byte,bit))
 for name,bad in [('truncated',chip[:-1]),('extended',chip+b'\0')]:
  try:v.check(bad,rom,log,'right_hold')
  except AssertionError:rejected.append(name)
  else:raise AssertionError(name)
 for field in ('cpu_model=68020','chipset=aga','fastmem_size=0','chipmem_size=4','bogomem_size=0','ntsc=false','cpu_cycle_exact=true','cpu_memory_cycle_exact=true','blitter_cycle_exact=true','JIT=0'):
  assert field in log
  try:v.check(chip,rom,log.replace(field,field+'INVALID'),'right_hold')
  except AssertionError:rejected.append('configuration '+field)
  else:raise AssertionError(field)
 for name,start,end in [('zero progression',0,d[9]),('zero render',d[8],d[8]),('wrapped invalid render',d[8],d[8]-1)]:
  bad=bytearray(chip);struct.pack_into('>II',bad,p+40,start,end)
  try:v.check(bytes(bad),rom,log,'right_hold')
  except AssertionError:rejected.append(name)
  else:raise AssertionError(name)
 with tempfile.TemporaryDirectory() as t:
  path=Path(t)/'bad.png';im=Image.open(out/'screen.ppm');im.putpixel((40,18),(255,0,0));im.save(path)
  try:v.display.verify_screen(chip,path)
  except AssertionError:rejected.append('actual viewport pixel')
  else:raise AssertionError('Pixel mutation accepted')
 result=dict(status='PASS',real_target_baseline=True,mutations_rejected=len(rejected),copper_terminator_single_bit_mutations_rejected=32,cases=rejected)
 (v.OUT/'rejection.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(rejected),'capture/configuration/video mutations rejected')
if __name__=='__main__':main()
