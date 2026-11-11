"""Read-only comparison of private original diagnostics and native jump replay."""
import sys,json
from pathlib import Path
def main():
 probes,native=map(Path,sys.argv[1:3]);runs={k:json.loads((probes/k/'result.json').read_text()) for k in ('early','grounded','right_control')};d=next(json.loads(l) for l in (native/'run.log').read_text().splitlines() if l.startswith('{"'))
 assert d['frame_goal']==90 and d['goal_reached'] and d['unsupported_boundary'] is None and d['completed_game_frames']==90
 fields={'active':(0x4d0,), 'action':(0x54,), 'edge':(0x14,), 'held':(0x16,), 'x':(0x4f0,0x500),'y':(0x510,0x520),'velocity':(0x550,0x560)}
 def trajectory(run):
  result=[]
  for r in run['rows']:
   if r['pc']!='0xc77b':continue
   row=dict(frame=r['frame'],nmi=r['nmi'])
   for key,addresses in fields.items():row[key]=sum(r['ram'][hex(a)]<<(8*i) for i,a in enumerate(addresses))
   result.append(row)
  return result
 original=trajectory(runs['grounded']);assert original==d['player_trajectory']
 baseline=trajectory(runs['right_control']);early=trajectory(runs['early']);assert len(baseline)==len(original)==91
 assert [(r['x'],r['y'],r['action']) for r in early]==[(r['x'],r['y'],r['action']) for r in baseline]
 gate=d['jump_gates'];assert len(gate)==1 and gate[0]['frame']==25 and gate[0]['edge']==128 and gate[0]['active']==128 and gate[0]['action']==0
 assert original[25]['y']==1460 and min(r['y'] for r in original[25:46])==1426 and original[45]['y']==1460 and original[45]['action']==0
 assert all(r['y']==1460 for r in baseline[25:46])
 history=json.loads((native/'input_history.json').read_text());polls=[r for r in history if r['helper']==138];assert len(polls)==90
 assert all(r['pads']==[129 if 24<=r['game_frame']<30 else 1,0] for r in polls)
 assert not any(r['unknown'] for r in runs.values())
 summary={k:d[k] for k in ('advanced_calls','logical_NMIs','APU_writes','inert_rejections','completed_game_frames','goal_reached','unsupported_boundary')};summary.update(accepted_jump_frame=25,landing_frame=45,vertical_before=1460,vertical_apex=1426,upward_displacement=34,all91_original_native_frame_states_equal=True,early_edge_physics_equal_to_control=True)
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
