#!/usr/bin/env python3
"""Bounded negative tests for both private first-music target checkpoints.

Requires eleven actual target dumps and hash-checked original cartridge.
No ROM, dump, or captured state is embedded. Positive baselines run first.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT/'port/tests/verify_recovery_reset_probe.py'
OLD = ['reset','first-yield','nmi-audio-entry','audio-reset','nmi-return',
       'scheduler-resume','resumed-task-setup','palette-nmi','music07']
NEW = ['music-fetch','music-command04']
NAMES = OLD+NEW

def verify(name, path):
    return subprocess.run([sys.executable,str(VERIFY),
        *([] if name=='reset' else ['--'+name]),str(path)],
        capture_output=True,timeout=30)

def dump(name):
    return ROOT/f'port/build/recovery-{name}-probe-chip.bin'

def build_isolation():
    """Eight old source-only modes need no input; all private modes fail closed."""
    with tempfile.TemporaryDirectory(prefix='first-music-build-') as tmp:
        root=Path(tmp)
        for directory in ('src','tools'):
            shutil.copytree(ROOT/'port'/directory,root/'port'/directory)
        builder=root/'port/tools/build_recovery_reset_probe.py'
        for name in OLD[:-1]:
            args=[] if name=='reset' else ['--'+name]
            subprocess.run([sys.executable,str(builder),*args],check=True,capture_output=True,timeout=30)
            for extension in ('bin','adf'):
                file=f'recovery-{name}-probe.{extension}'
                assert (root/'port/build'/file).read_bytes()==(ROOT/'port/build'/file).read_bytes()
        for wrong_input in (False,True):
            if wrong_input:
                (root/'input').mkdir()
                (root/'input/rescue-rangers-europe.nes').write_bytes(bytes(32))
            for name in ['music07',*NEW]:
                result=subprocess.run([sys.executable,str(builder),'--'+name],capture_output=True,timeout=30)
                assert result.returncode!=0
                assert not (root/'port/build/recovery-music07-private-bank3.bin').exists()
                assert not (root/'port/build'/f'recovery-{name}-probe.adf').exists()
    return {'source_only_modes_without_ROM':8,'missing_or_wrong_ROM_rejections':6}

def main():
    os.chdir(ROOT)
    for name in NAMES:
        result=verify(name,dump(name))
        assert result.returncode==0,(name,result.stderr.decode())
    isolation=build_isolation()
    report={'positive_baselines':len(NAMES),'build_isolation':isolation,'modes':{}}
    for name,marker in zip(NEW,(b'CDRRMFT1',b'CDRMC041')):
        data=dump(name).read_bytes();offset=data.index(marker)
        fields=struct.unpack_from('>21I' if name==NEW[1] else '>20I',data,offset+8)
        status,steps,ram,ctx,mapper,video,stack,end,sp,yieldp,nmi,entry,apu,restore,controller,palette,music_entry,music_apu,resource,fetch=fields[:20]
        ranges=[(ram,2048),(ctx,8),(mapper,82),(video,8754),(stack,4096),
                (yieldp,6),(nmi,298),(entry,22),(apu,30),(restore,22),(controller,74),
                (palette,454),(music_entry,22),(music_apu,30),(resource,16384),(fetch,6)]
        if name==NEW[1]:ranges.append((fields[20],14))
        positions=set(range(offset,offset+8+4*len(fields)))|set(range(ctx,ctx+8))
        # All guard bytes and all new read-journal bytes, plus complete two DMA snapshots.
        for address,size in ranges:
            positions.update(range(address-16,address));positions.update(range(address+size,address+size+16))
        for address,size in [(fetch,6),*( [(fields[20],14)] if name==NEW[1] else []),
                             (music_entry,22),(music_apu,30),(controller,74),
                             (nmi+42,256),(palette+198,256)]:
            positions.update(range(address,address+size))
        for address,size in ranges:
            if address!=stack:positions.update((address,address+size//2,address+size-1))
        positions.update(ram+a for a in [0,0x18,0x80,*range(0xc0,0xe4),*range(0x1a0,0x1c0),*range(0x753,0x778)])
        positions.update(resource+i for i in [0,1,0x48b,0x48c,0x22c1,0x22c2,16383,*range(0,16384,257)])
        jobs=[('bit',at,None) for at in sorted(positions)]
        # Every private resource/journal pointer aliases each existing buffer and both bounds.
        for field in [72,76,80,84]+([88] if name==NEW[1] else []):
            own=struct.unpack_from('>I',data,offset+field)[0]
            for destination in [0,len(data)-1,*[a for a,_ in ranges if a!=own]]:
                jobs.append(('pointer',offset+field,destination))
        with tempfile.TemporaryDirectory(prefix='first-music-negative-') as tmp:
            def reject(item):
                index,(kind,at,value)=item
                changed=bytearray(data)
                if kind=='bit':changed[at]^=1
                else:struct.pack_into('>I',changed,at,value)
                file=Path(tmp)/f'{index}.bin';file.write_bytes(changed)
                result=verify(name,file);file.unlink()
                assert result.returncode!=0,(name,kind,at,value)
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(reject,enumerate(jobs)))
        cross=0
        for other in NAMES:
            if other==name:continue
            assert verify(other,dump(name)).returncode!=0
            assert verify(name,dump(other)).returncode!=0
            cross+=2
        report['modes'][name]={'corruption_rejections':len(positions),
            'alias_range_rejections':len(jobs)-len(positions),'cross_mode_rejections':cross}
    output=ROOT/'logs/recovery-first-music-target-negative.json'
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
