#!/usr/bin/env python3
"""Isolated build reproducibility, legacy-byte preservation and private input gates."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile
PORT=Path(__file__).resolve().parents[1]
MODES=['reset','first-yield','nmi-audio-entry','audio-reset','nmi-return','scheduler-resume','resumed-task-setup','palette-nmi','music07','music-fetch','music-command04','music-channel-setup','music-first-channel']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def invoke(root,mode=None,new=False,ok=True):
    cmd=[sys.executable,str(root/'port/tools'/('build_recovery_runtime_probe.py' if new else 'build_recovery_reset_probe.py'))]
    if mode and mode!='reset':cmd+=['--'+mode]
    result=subprocess.run(cmd,capture_output=True,text=True)
    assert (result.returncode==0)==ok,(cmd,result.stdout,result.stderr)
    return result

def main():
    protected=list((PORT/'build').glob('recovery-*-probe*'))
    protected=[p for p in protected if p.is_file() and 'runtime' not in p.name]
    protected+=list((PORT.parent/'input').glob('*'))
    protected+=list((PORT.parent/'artifacts').rglob('*'))
    protected+=[PORT/'build/rescue-rangers-title.adf']
    # Protect published source and this driver's dependencies. Unrelated new
    # work may be developed concurrently and is deliberately outside this test.
    tracked=subprocess.check_output(['git','ls-files','port/src'],cwd=PORT.parent,text=True).splitlines()
    protected+=[PORT.parent/name for name in tracked]
    import importlib.util
    spec=importlib.util.spec_from_file_location('runtime_builder',PORT/'tools/build_recovery_runtime_probe.py')
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    protected+=[PORT/'src'/(name+'.s') for name in builder.NAMES]
    protected=list(dict.fromkeys(protected))
    protected=[p for p in protected if p.is_file()]
    before={str(p):digest(p) for p in protected}
    original_rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    with tempfile.TemporaryDirectory(prefix='runtime-build-isolation-') as tmp:
        root=Path(tmp);(root/'port/tools').mkdir(parents=True)
        shutil.copytree(PORT/'src',root/'port/src')
        for file in ('build_recovery_reset_probe.py','build_recovery_runtime_probe.py'):
            shutil.copyfile(PORT/'tools'/file,root/'port/tools'/file)
        # Positive baseline: all thirteen old payload/ADF pairs and new payload/ADF.
        (root/'input').mkdir();rom=root/'input/rescue-rangers-europe.nes';rom.write_bytes(original_rom)
        for mode in MODES:
            invoke(root,mode)
            for ext in ('bin','adf'):
                name=f'recovery-{mode}-probe.{ext}'
                assert digest(root/'port/build'/name)==digest(PORT/'build'/name),name
        invoke(root,new=True)
        for ext in ('bin','adf'):
            name='recovery-runtime-probe.'+ext
            assert digest(root/'port/build'/name)==digest(PORT/'build'/name),name
        # A second independent source-only tree has no cartridge at all.
        root2=root/'source-only';(root2/'port/tools').mkdir(parents=True)
        shutil.copytree(PORT/'src',root2/'port/src')
        for file in ('build_recovery_reset_probe.py','build_recovery_runtime_probe.py'):
            shutil.copyfile(PORT/'tools'/file,root2/'port/tools'/file)
        for mode in MODES[:8]:
            invoke(root2,mode)
            for ext in ('bin','adf'):
                name=f'recovery-{mode}-probe.{ext}'
                assert digest(root2/'port/build'/name)==digest(PORT/'build'/name),name
        shutil.rmtree(root2/'port/build')
        for wrong in (False,True):
            if wrong:
                (root2/'input').mkdir();(root2/'input/rescue-rangers-europe.nes').write_bytes(bytes(len(original_rom)))
            for mode in MODES[8:]:
                invoke(root2,mode,ok=False)
                assert not list((root2/'port/build').glob('*')),('Private legacy output on failed ROM',wrong,mode)
            invoke(root2,new=True,ok=False)
            assert not list((root2/'port/build').glob('*')),('Private runtime output on failed ROM',wrong)
    assert before=={str(p):digest(p) for p in protected},'Historical artifact/input modified'
    # Generated private driver/extract/disk/dumps must remain ignored.
    private=[PORT/'build'/n for n in ('recovery-runtime-private-driver.s','recovery-runtime-private-boot.s','recovery-runtime-private-bank3.bin','recovery-runtime-probe.bin','recovery-runtime-probe.adf','recovery-runtime-probe-chip.bin')]
    result=subprocess.run(['git','check-ignore',*map(str,private)],cwd=PORT.parent,capture_output=True,text=True)
    assert result.returncode==0 and len(result.stdout.splitlines())==len(private),result.stderr
    report=dict(status='PASS',legacy_payload_adf_pairs_byte_identical=13,source_only_modes_without_rom=8,private_modes_missing_and_wrong_rom_rejected=12,independent_runtime_build_reproducible=True,private_artifacts_ignored=len(private),historical_artifacts_and_inputs_unchanged=len(before))
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
