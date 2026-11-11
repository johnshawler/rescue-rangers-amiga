#!/usr/bin/env python3
"""Isolated deterministic builds and preservation checks for private stock CHR/fade diagnostics."""
import argparse, hashlib, importlib.util, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
PORT=Path(__file__).resolve().parents[1]
OUT=PORT/'build/chr-fade-stock'
BUILDER=PORT/'tools/build_recovery_resident_chr_fade_probe.py'
DELIVERED_SHA='6ffec7c18b1eef69c70048fc84a0b19f0a3daf2b34d67ae98fdb3fbcc765eb17'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preservation-inventory',type=Path,help='Optional earlier file/hash inventory to verify as well')
    parser.add_argument('--delivered-adf',type=Path,help='Optional supplied historical disk, checked against its approved hash')
    args=parser.parse_args()
    tracked=subprocess.check_output(['git','ls-files'],cwd=PORT.parent,text=True).splitlines()
    historical=[PORT.parent/name for name in tracked if (PORT.parent/name).is_file()]
    for directory in (PORT/'build',PORT.parent/'input',PORT.parent/'artifacts'):
        historical.extend(p for p in directory.rglob('*') if p.is_file() and OUT not in p.parents and '__pycache__' not in p.parts)
    prior={str(p.relative_to(PORT.parent)):digest(p) for p in set(historical)}
    if args.preservation_inventory:
        earlier=json.loads(args.preservation_inventory.read_text())
        for name,expected in earlier.items():
            assert (PORT.parent/name).is_file() and digest(PORT.parent/name)==expected,('Earlier historical file changed',name)
        prior.update(earlier)
    def preserved():
        for name,expected in prior.items():
            path=PORT.parent/name
            assert path.is_file() and digest(path)==expected,('Historical file changed',name)
        if args.delivered_adf:assert digest(args.delivered_adf)==DELIVERED_SHA,'Delivered ADF changed'
    preserved()
    spec=importlib.util.spec_from_file_location('stock_chr_builder',BUILDER)
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    dependencies=[BUILDER,PORT/'tests/recovery_resident_chr_fade_target_oracle.py',PORT/'src/boot.s']+[PORT/'src'/(n+'.s') for n in builder.NAMES]
    target_tests=[PORT/'tests'/name for name in ('test_recovery_resident_chr_fade_build.py','verify_recovery_resident_chr_fade_probe.py','test_recovery_resident_chr_fade_probe_rejection.py')]
    before={p:digest(p) for p in dependencies+target_tests}
    published=json.loads((OUT/'build.json').read_text())
    assert published['source_sha256']=={str(p.relative_to(PORT)):before[p] for p in dependencies},'Build source manifest is stale or incomplete'
    original=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    def run(root,success):
        env=dict(os.environ)
        # Retain only external installed dependencies, never this checkout.
        env['PYTHONPATH']=os.pathsep.join(p for p in env.get('PYTHONPATH','').split(os.pathsep) if p and Path(p).is_absolute() and Path(p).resolve()!=PORT.parent and PORT.parent not in Path(p).resolve().parents)
        proc=subprocess.run([sys.executable,str(root/'port/tools'/BUILDER.name)],cwd=root,env=env,capture_output=True,text=True)
        assert (proc.returncode==0)==success,(proc.stdout,proc.stderr)
        return proc
    with tempfile.TemporaryDirectory(prefix='stock-chr-fade-build-') as temporary:
        root=Path(temporary)
        for source in dependencies:
            destination=root/'port'/source.relative_to(PORT)
            destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
        isolated=root/'port/build/chr-fade-stock'
        run(root,False);assert not (root/'port/build').exists(),'Missing ROM wrote output'
        cartridge=root/'input/rescue-rangers-europe.nes';cartridge.parent.mkdir()
        cartridge.write_bytes(bytes(len(original)))
        run(root,False);assert not (root/'port/build').exists(),'Wrong ROM wrote output'
        cartridge.write_bytes(original);run(root,True)
        generated=sorted(p.name for p in isolated.iterdir())
        first={name:digest(isolated/name) for name in generated}
        assert first=={name:digest(OUT/name) for name in generated},'Isolated generated files differ'
        assert len(generated)==23 and len([n for n in generated if n.endswith('.adf')])==4
        run(root,True)
        assert generated==sorted(p.name for p in isolated.iterdir())
        assert first=={name:digest(isolated/name) for name in generated},'Repeat build differs'
        # Invalid input after a successful build must preserve every output too.
        cartridge.write_bytes(bytes(len(original)));run(root,False)
        assert first=={name:digest(isolated/name) for name in generated},'Wrong ROM overwrote output'
        cartridge.unlink();run(root,False)
        assert first=={name:digest(isolated/name) for name in generated},'Missing ROM overwrote output'
    preserved()
    assert before=={p:digest(p) for p in before},'Target source dependency changed'
    ignored=subprocess.run(['git','check-ignore',*[str(OUT/n) for n in generated]],cwd=PORT.parent,capture_output=True,text=True)
    assert ignored.returncode==0 and len(ignored.stdout.splitlines())==len(generated),'Private outputs not ignored'
    report=dict(status='PASS',isolated_build=True,repeat_build_identical=True,generated_files_compared=len(generated),private_ADFs=4,missing_and_wrong_ROM_fail_before_output=True,missing_and_wrong_ROM_preserve_existing_outputs=True,historical_files_unchanged=len(prior),delivered_ADF_checked=bool(args.delivered_adf),delivered_ADF_check='PASS' if args.delivered_adf else 'not supplied',delivered_ADF_sha256=DELIVERED_SHA if args.delivered_adf else None,earlier_inventory_checked=bool(args.preservation_inventory),exact_build_source_manifest_verified=True,build_dependencies_protected=len(dependencies),target_test_source_protected=True,private_outputs_ignored=len(generated),maximum_allocation_bytes=published['maximum_allocation_bytes'],generated_sha256=first)
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
