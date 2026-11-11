#!/usr/bin/env python3
"""Negative target validation and isolated authorized-input reproducible build."""
from pathlib import Path
import json,os,shutil,struct,subprocess,sys,tempfile
from verify_recovery_stage_resource_probe import PORT,references,verify
NAME='recovery-stage-resource-probe'
def main():
    original=(PORT/'build'/f'{NAME}-chip.bin').read_bytes();refs=references();baseline=verify(original,refs)
    positions=set(range(baseline['header'],baseline['header']+40));pointer_fields=[]
    for r in baseline['records']:pointer_fields.extend(r+i for i in range(0,48,4))
    pointer_fields.extend(baseline['header']+16+i*4 for i in range(6))
    for address,size,kind in baseline['ranges']:
        if kind=='header':continue
        if kind=='native stack':
            positions.update(range(address,address+16));positions.update(range(address+size-16,address+size));positions.add(address+16)
        else:positions.update(range(address,address+size))
    def reject(data):
        try:verify(data,refs)
        except (AssertionError,struct.error):return
        raise AssertionError('corruption accepted')
    for at in sorted(positions):
        changed=bytearray(original);changed[at]^=1;reject(changed)
    aliases=0
    destinations=[0,1,len(original)-1,0xffffffff,baseline['header'],*baseline['records']]
    destinations.extend(a+16 for a,n,k in baseline['ranges'] if k!='header')
    for at in pointer_fields:
        own=struct.unpack_from('>I',original,at)[0]
        for destination in sorted(set(destinations)-{own}):
            changed=bytearray(original);struct.pack_into('>I',changed,at,destination);reject(changed);aliases+=1
    reject(original[:-1]);reject(original+b'\x00')
    with tempfile.TemporaryDirectory(prefix='stage-private-input-') as tmp:
        root=Path(tmp)/'port'
        files=['src/boot.s','src/recovery_gameplay_player_init.s','src/recovery_gameplay_fade_entry.s',
               'src/recovery_stage_resource_init.s','src/recovery_stage_resource_probe.s',
               'tests/recovery_stage_resource_target_fixtures.py','tools/build_recovery_stage_resource_probe.py']
        for f in files:
            dest=root/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(PORT/f,dest)
        command=[sys.executable,str(root/'tools/build_recovery_stage_resource_probe.py')]
        before={p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
        missing=subprocess.run(command,capture_output=True);assert missing.returncode and not (root/'build').exists()
        assert {p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}==before
        inp=Path(tmp)/'input';inp.mkdir();rom=inp/'rescue-rangers-europe.nes';rom.write_bytes(b'wrong cartridge')
        wrong=subprocess.run(command,capture_output=True);assert wrong.returncode and not (root/'build').exists()
        assert {p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}==before
        shutil.copyfile(PORT.parent/'input/rescue-rangers-europe.nes',rom)
        subprocess.run(command,check=True,capture_output=True)
        report=json.loads((root/'build'/f'{NAME}-build.json').read_text());assert report['proprietary_inputs'] is True
        for ext in ('bin','adf'):
            assert (root/'build'/f'{NAME}.{ext}').read_bytes()==(PORT/'build'/f'{NAME}.{ext}').read_bytes()
    result=dict(positive_compositions=6,byte_corruption_rejections=len(positions),pointer_rejections=aliases,size_rejections=2,authorized_input_rebuild_identical=True,missing_rom_rejected_before_output=True,wrong_rom_rejected_before_output=True)
    (PORT.parent/'logs/recovery-stage-resource-negative.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
