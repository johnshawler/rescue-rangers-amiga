#!/usr/bin/env python3
"""Freeze generic source closure only, never ROM/captures/disks/profiles."""
import argparse,ast,hashlib,json,re,sys,tarfile
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parent
sys.path.insert(0,str(P/'tests'))
from recovery_state_menu_sfx_harness import SOURCES
from recovery_state_menu_sfx_models import NAMES as MODEL_NAMES

def package(out):
 out.mkdir(parents=True,exist_ok=False)
 assembly={P/'src'/f'{n}.s' for n in SOURCES}|{P/'src/recovery_state_menu_display_device.s'}
 chosen=set();pending=[*P.glob('src/recovery_menu_paula_*'),*P.glob('tools/recovery_menu_paula_*'),*P.glob('tests/recovery_menu_paula_*'),*P.glob('analysis/recovery_menu_paula_*')]
 pending += [*P.glob('src/recovery_live_*'),*P.glob('tools/recovery_live_*'),*P.glob('tests/recovery_live_*'),*P.glob('analysis/recovery_live_*'),*P.glob('src/recovery_redraw_*'),*P.glob('tests/recovery_redraw_*'),*P.glob('analysis/recovery_redraw_*'),*P.glob('src/recovery_scene_continue_*'),*P.glob('tests/recovery_scene_continue_*'),*P.glob('analysis/recovery_scene_continue_*'),P/'src/recovery_zx_keyboard.s']
 assembly.update(pending)
 pending += [P/'src'/f'{n}.s' for n in SOURCES]
 pending += [P/'tests'/f'recovery_test_{n}.py' for n in MODEL_NAMES]
 pending += [ROOT/'tools/test_menu_paula_public.sh',ROOT/'validate_menu_paula.sh',ROOT/'requirements-dev.txt',P/'src/boot.s',P/'src/recovery_menu_sfx_target.s',P/'src/recovery_state_menu_display_device.s',P/'src/experimental_direct_paula.c',P/'src/experimental_direct_paula.h',P/'tools/experimental_paula_headless.c',P/'analysis/recovery_state_menu_sfx_manifest.json',P/'analysis/recovery_menu_sfx_target_dependencies.json']
 while pending:
  path=pending.pop().resolve()
  if path in chosen:continue
  assert path.is_file() and path.is_relative_to(ROOT) and not path.is_relative_to(P/'build'),str(path)
  chosen.add(path);s=path.read_text()
  if path.suffix=='.py':
   for node in ast.walk(ast.parse(s)):
    mods=[n.name for n in node.names] if isinstance(node,ast.Import) else [node.module] if isinstance(node,ast.ImportFrom) else []
    for mod in mods:
     if not mod:continue
     for folder in ('tests','tools'):
      q=P/folder/(mod.split('.')[0]+'.py')
      if q.exists():pending.append(q)
  if path in assembly:
   for name in re.findall(r'^\s*include\s+"([^"]+)"',s,re.M):
    q=P/'src'/name;assembly.add(q);pending.append(q)
  if path.name in ('recovery_state_menu_sfx_manifest.json','recovery_menu_sfx_target_dependencies.json'):
   j=json.loads(s)
   if isinstance(j,dict):
    for entry in j.get('files',[])+j.get('frozen_dependencies',[]):
     if 'path' in entry:pending.append(ROOT/entry['path'])
  if path.name=='recovery_scene_continue_manifest.json':
   j=json.loads(s);pending += [ROOT/x for x in j['source_hashes']]+[ROOT/x for x in j['frozen_dependencies']]
 files=[]
 for path in sorted(chosen):
  data=path.read_bytes();files.append(dict(path=str(path.relative_to(ROOT)),size=len(data),sha256=hashlib.sha256(data).hexdigest()))
 manifest={'classification':'generic source only; no copyrighted input or derived playback fixtures','files':files}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 with tarfile.open(out/'source-only.tar.gz','w:gz') as tar:
  for path in sorted(chosen):tar.add(path,arcname=str(path.relative_to(ROOT)))
  tar.add(out/'manifest.json',arcname='recovery_live_source_manifest.json')
 print(json.dumps({'files':len(files),'archive_sha256':hashlib.sha256((out/'source-only.tar.gz').read_bytes()).hexdigest()}))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('output',type=Path);v=a.parse_args();package(v.output.resolve())
