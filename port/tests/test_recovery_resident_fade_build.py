#!/usr/bin/env python3
"""Private isolated reproducibility and unchanged historical inputs/artifacts."""
from pathlib import Path
import hashlib,importlib.util,json,os,shutil,subprocess,sys,tempfile
PORT=Path(__file__).resolve().parents[1]
NAME='recovery-resident-fade'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    # Snapshot every existing historical output and original input/firmware,
    # plus all tracked files. Do not include unrelated unpublished worker files.
    protected=[]
    for directory in (PORT/'build',PORT.parent/'input',PORT.parent/'artifacts'):
        protected.extend(p for p in directory.rglob('*') if p.is_file() and NAME not in p.name)
    tracked=subprocess.check_output(['git','ls-files'],cwd=PORT.parent,text=True).splitlines()
    protected.extend(PORT.parent/p for p in tracked if (PORT.parent/p).is_file())
    # Explicitly protect this target's unpublished implementation as well.
    # Import its builder to obtain the exact helper list, not a broad glob of
    # other workers' unpublished source. Capture its in-repository Python
    # imports so reference-only dependency files are protected transitively.
    target_files=[PORT/name for name in (
        'tools/build_recovery_resident_fade_probe.py',
        'tests/recovery_resident_fade_target_oracle.py',
        'tests/verify_recovery_resident_fade_probe.py',
        'tests/test_recovery_resident_fade_build.py',
        'tests/test_recovery_resident_fade_probe_rejection.py')]
    prior_modules=set(sys.modules)
    spec=importlib.util.spec_from_file_location('resident_fade_builder',target_files[0])
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    helper_sources=[PORT/'src'/(name+'.s') for name in builder.NAMES]
    reference_dependencies=[]
    for name in set(sys.modules)-prior_modules:
        file=getattr(sys.modules[name],'__file__',None)
        if file:
            path=Path(file).resolve()
            if path.suffix=='.py' and PORT in path.parents:
                reference_dependencies.append(path)
    explicit=target_files+helper_sources+reference_dependencies+[PORT/'src/boot.s']
    assert all(p.is_file() for p in explicit),'Missing target preservation dependency'
    protected.extend(explicit)
    before={p:digest(p) for p in set(protected)}
    original=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    def run(root,ok=True):
        env=dict(os.environ)
        # No fallback to this original checkout: only explicitly configured
        # installed dependencies may be supplied through PYTHONPATH.
        env['PYTHONPATH']=os.pathsep.join(p for p in env.get('PYTHONPATH','').split(os.pathsep) if p and Path(p).is_absolute() and PORT.parent not in Path(p).resolve().parents)
        result=subprocess.run([sys.executable,str(root/'port/tools/build_recovery_resident_fade_probe.py')],cwd=root,env=env,capture_output=True,text=True)
        assert (result.returncode==0)==ok,(result.stdout,result.stderr)
    with tempfile.TemporaryDirectory(prefix='resident-fade-build-') as temporary:
        root=Path(temporary)
        (root/'port/tools').mkdir(parents=True)
        shutil.copytree(PORT/'src',root/'port/src')
        shutil.copytree(PORT/'tests',root/'port/tests',ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copyfile(PORT/'tools/build_recovery_resident_fade_probe.py',root/'port/tools/build_recovery_resident_fade_probe.py')
        # Missing and invalid private cartridges fail before any output exists.
        run(root,False);assert not (root/'port/build').exists()
        (root/'input').mkdir();rom=root/'input/rescue-rangers-europe.nes'
        rom.write_bytes(bytes(len(original)));run(root,False);assert not (root/'port/build').exists()
        rom.write_bytes(original);run(root)
        generated=list((root/'port/build').iterdir())
        for artifact in generated:
            assert digest(artifact)==digest(PORT/'build'/artifact.name),artifact.name
        # Independent rerun remains bit-for-bit deterministic.
        first={p.name:digest(p) for p in generated}
        run(root)
        assert first=={p.name:digest(p) for p in generated}
    # The established test rebuilds all 13 old modes and frozen 68-call probe.
    old=subprocess.run([sys.executable,str(PORT/'tests/test_recovery_runtime_build.py')],cwd=PORT.parent,capture_output=True,text=True)
    assert old.returncode==0,(old.stdout,old.stderr)
    assert before=={p:digest(p) for p in before},'Historical artifact, input or explicit target dependency changed'
    private=list((PORT/'build').glob(NAME+'*'))
    ignored=subprocess.run(['git','check-ignore',*map(str,private)],cwd=PORT.parent,capture_output=True,text=True)
    assert ignored.returncode==0 and len(ignored.stdout.splitlines())==len(private)
    print(json.dumps(dict(status='PASS',isolated_build=True,repeat_build_identical=True,
        generated_files_compared=len(generated),missing_and_wrong_ROM_fail_closed=True,
        legacy_payload_ADF_pairs_identical=13,frozen_68_call_build_identical=True,
        historical_and_target_files_unchanged=len(before),
        explicit_target_files_protected=len(target_files),helper_sources_protected=len(helper_sources),
        reference_python_dependencies_protected=len(set(reference_dependencies)),
        private_outputs_ignored=len(private)),indent=2))
if __name__=='__main__':main()
