#!/usr/bin/env python3
"""Actual 68k/original ordered-effects replay, plus new title-helper guards."""
from pathlib import Path
import tempfile,subprocess,os,struct,sys,json
from recovery_state_menu_sfx_harness import Native,SOURCES,PORT,CTX,RUNTIME,RAM
from recovery_live_oracle import oracle
b=Path(sys.argv[1]);chip=(b/'full-CHIP.bin').read_bytes();f=struct.unpack_from('>21I',chip,chip.index(b'CDRSFX01')+8);live=struct.unpack_from('>9I',chip,chip.index(b'CDRCLIV1')+8)
changes=[struct.unpack_from('>4I',chip,live[4]+i*16) for i in range(live[5])]
cfg=json.loads((b/'build.json').read_text());scene=cfg.get('scene',False)
if scene:
 from recovery_scene_continue_harness import SOURCES
source=(PORT/'src/recovery_live_dispatch.s').read_text().replace('bne.l recovery_state_menu_sfx','bne.l recovery_scene_continue_dispatch' if scene else 'bne.l recovery_state_menu_sfx')+'\n'+'\n'.join((PORT/'src'/f'{n}.s').read_text() for n in SOURCES)
with tempfile.TemporaryDirectory() as t:
 p=Path(t);(p/'test.s').write_text(source);subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(p/'test.bin'),str(p/'test.s')],check=True);code=(p/'test.bin').read_bytes()
rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();native=Native(code,rom[16:131088]);ref=oracle(rom,changes,f[1],native,scene)
assert native.snapshot()[0]==chip[f[4]:f[4]+2048]
# Guard failures are inert from a valid synthetic title state.
r=bytearray(2048);r[0x80]=2;c=bytes.fromhex('a055274000a4bda7');rt=bytes.fromhex('1e1f1f02000000480000d501')
native.restore((bytes(r),c,bytes(134638),rt))
for addr,value in [(CTX+5,b'\x30'),(RUNTIME,b'\x0c'),(RUNTIME+3,b'\x03'),(RUNTIME+4,b'\x01'),(RUNTIME+10,b'\x00'),(RAM+0x91,b'\x01'),(RAM+0x80,b'\x03')]:native.reject(addr,value)
native.reject(event=1)
assert native.run()==1
state=native.snapshot();assert state[0][0x1bd]==0xa0 and state[0][0x1bc]==0x24 and state[1]==bytes.fromhex('ff04274000a4bba7')
print(json.dumps(dict(status='PASS',calls=f[1],original_instructions=ref[2],ordered_RAM_and_device_effects_every_helper=True,continuous_native_state=True,new_helper_inert_guard_cases=8)))
