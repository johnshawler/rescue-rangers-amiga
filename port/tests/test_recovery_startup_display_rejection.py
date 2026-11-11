#!/usr/bin/env python3
"""Reject mutations of real positive target captures, never synthetic positives."""
from pathlib import Path
import struct,json
from verify_recovery_startup_display import check,PORT

def main():
 out=PORT/'build/startup-display-native';chip=(out/'chip.bin').read_bytes();rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();log=(out/'amiga.log').read_text()
 check(chip,rom,log)
 p=chip.index(b'CDRDIS01');f=struct.unpack_from('>10I',chip,p+8)
 cases=[('marker',p),('status',p+11)]
 for i,name in enumerate(('device','nt','palette','oam','chr','frame','copper'),1):
  cases.append((name+' pointer',p+8+4*i))
 for i in range(28):cases.append((f'device byte{i}',f[1]+i))
 for name,addr,n in [('nt',f[2],2048),('palette',f[3],32),('oam',f[4],256),('chr',f[5],8192),('frame',f[6],51200)]:
  for delta in sorted(set((0,n//2,n-1))):cases.append((f'{name} {delta}',addr+delta))
 for i in range(88):cases.append((f'copper setup byte{i}',f[7]+i))
 for i in range(32):cases.append((f'copper color{i}',f[7]+88+4*i+3))
 rejected=[]
 for name,off in cases:
  bad=bytearray(chip);bad[off]^=1
  try:check(bytes(bad),rom,log)
  except (AssertionError,ValueError,struct.error):rejected.append(name)
  else:raise AssertionError('Mutation not rejected: '+name)
 for field in ('cpu_model=68020','chipset=aga','fastmem_size=0'):
  assert field in log
  try:check(chip,rom,log.replace(field,field+'INVALID'))
  except AssertionError:rejected.append('configuration '+field)
  else:raise AssertionError('configuration accepted')
 report={'status':'PASS','real_target_baseline':True,'mutations_rejected':len(rejected),'cases':rejected}
 (out/'rejection.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(rejected),'real capture/configuration mutations rejected')
if __name__=='__main__':main()
