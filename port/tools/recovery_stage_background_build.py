#!/usr/bin/env python3
"""Additive uninstrumented target: substitute only the qualified background draw."""
from pathlib import Path
import argparse,hashlib,json,sys
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P/'tools'))
import recovery_stage_target_build as base
FREEZE='9a7a81f49acd1d11d93efab12feb2fd25677c4b84317774e1e96013f13b290f2'
CANDIDATE='d916fffbc90f750b96568fc85f4f069a1b6b4e8bff706cec7756b5c628c23f3e'
def prepare(s,out):
 d=(P/'src/recovery_stage_target_device.s').read_text()
 assert d.count(' bsr recovery_scroll_view_draw')==1
 assert d.count(' include "recovery_scroll_view_draw.s"')==1
 d=d.replace(' bsr recovery_scroll_view_draw',' bsr recovery_stage_background_draw')
 d=d.replace(' include "recovery_scroll_view_draw.s"',' include "recovery_stage_background_draw.s"')
 (out/'recovery_stage_background_device.s').write_text(d)
 a=' include "recovery_stage_target_device.s"';assert s.count(a)==1
 return s.replace(a,f' include "{out}/recovery_stage_background_device.s"',1)
def build(out):
 assert hashlib.sha256((P/'analysis/recovery_stage_target_manifest.json').read_bytes()).hexdigest()==FREEZE
 assert hashlib.sha256((P/'src/recovery_stage_background_draw.s').read_bytes()).hexdigest()==CANDIDATE
 original=base.integrated_source
 base.integrated_source=lambda *args:prepare(original(*args),out)
 try:base.build(out,'default',1,0)
 finally:base.integrated_source=original
 meta=json.loads((out/'build.json').read_text())
 meta.update(background_optimized=True,profiling=False,background_source_sha256=CANDIDATE,background_stage_freeze=FREEZE,background_max_stack_bytes=128)
 for path in (P/'src/recovery_stage_background_draw.s',Path(__file__).resolve()):
  meta['sources'][str(path.relative_to(P.parent))]=hashlib.sha256(path.read_bytes()).hexdigest()
 (out/'build.json').write_text(json.dumps(meta,indent=2)+'\n')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();build(a.output.resolve())
