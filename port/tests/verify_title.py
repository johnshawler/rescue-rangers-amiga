#!/usr/bin/env python3
"""Check actual Amiga RAM and video against independent original-ROM reference."""
from pathlib import Path
import json, struct, sys
import numpy as np
from PIL import Image

P=Path(__file__).resolve().parents[1]
L=P.parent
name=sys.argv[1] if len(sys.argv)>1 else 'title'
reference_name=sys.argv[2] if len(sys.argv)>2 else name
s=(P/'assets/title-snapshot.bin').read_bytes()
ram=(P/f'build/{name}-chip-ram.bin').read_bytes()
off=ram.find(b'CDRPORT1')
assert off>=0, 'Native boot report missing'
status,sprite_status,bg_ticks,sprite_ticks,fb,free_chip=struct.unpack_from('>6I',ram,off+8)
assert status == sprite_status == 0
config=(L/f'logs/amiga-{name}.log').read_text()
for required in ['cpu_model=68020','chipmem_size=4','fastmem_size=0','ntsc=false','cpu_cycle_exact=true','cpu_memory_cycle_exact=true','blitter_cycle_exact=true','JIT=0']:
    assert required in config, f'Missing verified target setting: {required}'
g=ram.find(b'CDRGAME1')
assert g>=0
game_status,game_ticks,game_ram,inputs=struct.unpack_from('>4I',ram,g+8)
assert game_status==0 and game_ticks>0
expected_edges={'title':0,'two-player':1,'character-chip':16,'character-dale':17,'handoff':17}[name]
assert (inputs>>8)&255 == expected_edges, f'Controller events missing: {inputs:08x}'
context=struct.unpack_from('>I',ram,g+24)[0]
phase=ram[context]
assert phase=={'title':1,'two-player':1,'character-chip':2,'character-dale':2,'handoff':3}[name]
assert ram[game_ram+0x50]==(1 if name in ('two-player','handoff') else 0)
assert ram[game_ram+0x92] == ((L/'artifacts/title-ram.bin').read_bytes()[0x92]+game_ticks)&255

assert 0 < fb < len(ram)-51200
pal,rgb=s[4:36],s[36:228]
colors=[]
for i in range(32):
    n=pal[i if i%4 else 0]&63
    colors.append(tuple((v>>4)*17 for v in rgb[n*3:n*3+3]))
indices=np.zeros((256,320),np.uint8)
planes=np.frombuffer(ram[fb:fb+51200],np.uint8).reshape((5,256,40))
for p in range(5):
    indices |= np.unpackbits(planes[p],axis=1).astype(np.uint8)<<p
rendered=np.array(colors,dtype=np.uint8)[indices]
ref=np.array(Image.open(L/f'artifacts/{reference_name}-reference.png').convert('RGB'))
assert ref.shape==(240,256,3)
ref=(ref>>4)*17
active=rendered[8:248,32:288]
reference_differences=int(np.count_nonzero(np.any(active!=ref,axis=2)))
assert reference_differences==0, f'{reference_differences} original NES reference pixel mismatches'
actual=np.array(Image.open(P/f'build/{name}-amiga.ppm').convert('RGB'))
expected=np.repeat(rendered,2,axis=1)
best=(expected.shape[0]*expected.shape[1]+1,None)
for y in range(actual.shape[0]-256+1):
    for x in range(0,actual.shape[1]-640+1,2):
        diff=int(np.count_nonzero(np.any(actual[y:y+256,x:x+640]!=expected,axis=2)))
        if diff<best[0]:best=(diff,[x,y])
assert best[0]==0, f'{best[0]} Amiga DMA display mismatches'
Image.fromarray(rendered).save(P/f'build/{name}-planar-decoded.png')
Image.open(P/f'build/{name}-amiga.ppm').save(P/f'build/{name}-amiga.png')
report={'native_boot_status':status,'native_sprite_status':sprite_status,
        'native_vs_original_nes_different_pixels':reference_differences,
        'display_vs_native_framebuffer_different_pixels':best[0],'display_offset':best[1],
        'free_chip_bytes':free_chip,
        'title_phase':phase,'native_game_selftest_status':game_status,'native_timer_ticks':game_ticks,
        'input_edges_seen_hex':f'{inputs & 0xffff:04x}',
        'isolated_background_eclock_ticks_display_dma_off':bg_ticks,
        'isolated_sprite_eclock_ticks_display_dma_off':sprite_ticks,
        'timing_limit':'Isolated static fixture, emulator target; not a gameplay or full-speed measurement'}
(P/f'build/{name}-target-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
