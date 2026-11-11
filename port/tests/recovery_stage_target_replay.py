#!/usr/bin/env python3
"""Private continuous native/original replay from actual CIA boundary records."""
from pathlib import Path
import os,sys,json,struct,subprocess,tempfile,hashlib
from recovery_bank_loader_music_harness import Native,SOURCES,PORT
from recovery_stage_target_oracle import oracle

def replay(b):
 chip=(b/'full-CHIP.bin').read_bytes()
 f=struct.unpack_from('>21I',chip,chip.index(b'CDRSFX01')+8)
 live=struct.unpack_from('>9I',chip,chip.index(b'CDRCLIV1')+8)
 changes=[struct.unpack_from('>4I',chip,live[4]+i*16) for i in range(live[5])]
 wrapper=(PORT/'src/recovery_live_dispatch.s').read_text().replace('bne.l recovery_state_menu_sfx','bne.l recovery_bank_loader_music_dispatch')
 source=wrapper+'\n'+'\n'.join((PORT/'src'/(n+'.s')).read_text() for n in SOURCES)
 with tempfile.TemporaryDirectory() as t:
  p=Path(t);(p/'host.s').write_text(source)
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(p/'host.bin'),str(p/'host.s')],check=True)
  code=(p/'host.bin').read_bytes()
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
 n=Native(code,rom[16:131088])
 ref=oracle(rom,changes,f[1],native=n)
 results,bus,instructions=ref
 assert n.snapshot()[0]==chip[f[4]:f[4]+2048] and n.snapshot()[1]==chip[f[5]:f[5]+8]
 assert n.snapshot()[3]==chip[f[7]:f[7]+12]
 result=dict(status='PASS',calls=len(results),original_instructions=instructions,actual_input_changes=changes,context=results[-1][2].hex(),native_sha256=hashlib.sha256(code).hexdigest(),ordered_effects_all_boundaries=True,all_RAM_context_runtime_boundaries=True,terminal_target_equal=True)
 (b/'stage-target-replay.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
 return ref
if __name__=='__main__':replay(Path(sys.argv[1]))
