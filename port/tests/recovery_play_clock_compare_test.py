#!/usr/bin/env python3
"""Source-only decision tests, no ROM or capture needed."""
from copy import deepcopy
from recovery_play_clock_compare import qualify,reductions,require
from recovery_audio_clock_model import ClockModel
from fractions import Fraction
m=ClockModel(Fraction(58204977075,16384),44100,41245.0234375)
n=dict(status='PASS',windows=[dict(RTI=i,margin=.2,minimum_shift_margin=.19,minimum_shift_correlation=.9) for i in range(380,384)],skipped_windows=[],threshold_correlation=.45,threshold_margin=.08,physical_guards_seconds=[.11,.02],phase_count_each_hypothesis=128,rate_factors=[1,.5,2],shift_checks=804)
t=dict(status='PASS',windows=[dict(RTI=i) for i in range(396,401)],physical_guards_seconds=[.11,.03],frequency_tolerance_hz=8,negative_checks=15)
bound=dict(status='PASS',legacy_nominal_clock_scale_error_remaining=False,total_corrected_placement_uncertainty_ms=2.18)
r=dict(status='PASS',immutable_capture_hashes={'x':'identity'},clock=m.describe(),runtime_clock_attestation={'stable':True},source_attestation={'source':'pinned'},noise=n,gameplay_tonal=t,endpoint_and_mapping_bound=bound)
v=dict(status='PASS',frame_screen={'status':'PASS'},runner_error=0,rtis=400,render_count=400,completed_game_frames=5,Fast_bytes=0,final_original_ram_context_runtime=True,last_journal_equal=True,retained_audio_records_equal=256)
replay=dict(status='PASS',ordered_effects_all_boundaries=True,all_RAM_context_runtime_boundaries=True,terminal_target_equal=True)
build=dict(display_dma=1,profiling=False,goal_game_frames=5)
def check(r,v,replay,build):qualify(r,m,{'stable':True},{'source':'pinned'},{'x':'identity'},v,replay,build)
check(r,v,replay,build);count=0
cases=[(0,('status',),'FAIL'),(0,('immutable_capture_hashes','x'),'other'),(0,('clock','callback_cia_hz'),709379),(0,('runtime_clock_attestation','stable'),False),(0,('source_attestation','source'),'other'),(0,('noise','status'),'FAIL'),(0,('noise','windows'),[]),(0,('noise','skipped_windows'),[383]),(0,('noise','threshold_margin'),.07),(0,('noise','threshold_correlation'),.44),(0,('noise','phase_count_each_hypothesis'),64),(0,('noise','physical_guards_seconds'),[.12,.02]),(0,('noise','shift_checks'),803),(0,('noise','rate_factors'),[1]),(0,('gameplay_tonal','status'),'FAIL'),(0,('gameplay_tonal','windows'),[]),(0,('gameplay_tonal','frequency_tolerance_hz'),9),(0,('gameplay_tonal','negative_checks'),14),(0,('endpoint_and_mapping_bound','legacy_nominal_clock_scale_error_remaining'),True),(0,('endpoint_and_mapping_bound','total_corrected_placement_uncertainty_ms'),3),(1,('status',),'FAIL'),(1,('frame_screen','status'),'FAIL'),(1,('runner_error',),-1),(1,('Fast_bytes',),1024),(1,('rtis',),399),(1,('retained_audio_records_equal',),255),(1,('final_original_ram_context_runtime',),False),(2,('ordered_effects_all_boundaries',),False),(2,('all_RAM_context_runtime_boundaries',),False),(2,('terminal_target_equal',),False),(3,('display_dma',),0),(3,('profiling',),True)]
for index,path,value in cases:
 args=deepcopy([r,v,replay,build]);obj=args[index]
 for key in path[:-1]:obj=obj[key]
 obj[path[-1]]=value
 try:check(*args)
 except ValueError:count+=1
 else:raise AssertionError(path)
a=dict(final_redraw_ticks=50,five_interval_ticks=60,progression_ticks=70);b={k:100 for k in a};h=dict(sha256='complete',helpers=3,instructions=9,changes=[[1,0,2,16]])
assert reductions(a,b,h,h,True)['final_redraw_ticks_reduction_percent']==50
for key,value in [('sha256','other'),('helpers',4),('instructions',10),('changes',[])]:
 other=dict(h);other[key]=value;out=reductions(a,b,h,other,True);assert not out['same_input_helper_history'] and not any('percent' in k for k in out)
try:reductions(a,b,h,h,False)
except ValueError:pass
else:raise AssertionError('Final mismatch admitted')
print('PASS: 32 qualification negatives; 4 complete-history mismatch suppressions; matched/final-state gates.')
import tempfile
from pathlib import Path
from recovery_audio_clock_model import verify_hashes,sha
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp);(p/'evidence').write_text('approved');pin={'evidence':sha(p/'evidence')};verify_hashes(p,pin)
 (p/'evidence').write_text('PASS but altered')
 try:verify_hashes(p,pin)
 except AssertionError:pass
 else:raise AssertionError('Altered evidence admitted')
 (p/'evidence').unlink()
 try:verify_hashes(p,pin)
 except FileNotFoundError:pass
 else:raise AssertionError('Missing evidence admitted')
print('PASS: altered/missing evidence rejection.')
