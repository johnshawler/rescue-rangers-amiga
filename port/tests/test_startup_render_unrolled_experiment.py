#!/usr/bin/env python3
"""Run retained independent pixel/ABI/guard tests on baseline and additive candidates.
Original tests are loaded read-only. Substitution chooses source and random seed,
never the reference logic. No cartridge data or timing claims.
"""
from pathlib import Path
import json
PORT=Path(__file__).resolve().parents[1]

def main():
 results=[]
 for kind,original,candidate,seeds in [
  ('background','native_background.s','native_background_unrolled_experiment.s',(68020,1,982451653)),
  ('sprites','native_sprite_blitter.s','native_sprite_emptyrow_experiment.s',(1200,1,982451653))]:
  test=PORT/'tests'/('test_native_background.py' if kind=='background' else 'test_native_sprites.py')
  source=test.read_text()
  for renderer in ((original,candidate,'native_background_paired_experiment.s','native_background_compact_experiment.s') if kind=='background' else (original,candidate)):
   for seed in seeds:
    selected=source.replace("src/"+original,"src/"+renderer)
    selected=selected.replace('random.Random(68020)',f'random.Random({seed})').replace('random.Random(1200)',f'random.Random({seed})')
    scope={'__file__':str(test),'__name__':'experiment_suite'}
    exec(compile(selected,str(test),'exec'),scope)
    scope['main']()
    results.append({'renderer':renderer,'seed':seed,'cases':7 if kind=='background' else 20,'status':'PASS'})
 out=PORT/'build/startup-render-unrolled-experiment';out.mkdir(parents=True,exist_ok=True)
 report={'status':'PASS','total_assembled_cases':sum(r['cases'] for r in results),'runs':results,'timing_claim':False}
 (out/'synthetic-tests.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
