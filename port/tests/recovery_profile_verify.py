#!/usr/bin/env python3
"""All predecessor semantic/audio assertions; exclude only named live profiler counters."""
from pathlib import Path
import argparse,hashlib
from recovery_profile_report import report
P=Path(__file__).resolve().parent

def verify(out):
 path=P/'recovery_menu_paula_verify.py';s=path.read_text()
 assert hashlib.sha256(path.read_bytes()).hexdigest()=='25808ce3b92b3936eb82dc24f670ea13bbdcd4ad68d86c0681f6c4093ece3d66'
 old="assert chip.count(immutable)==1,'compiled adapter/planner/wave data altered'"
 assert s.count(old)==1
 s=s.replace(old,"""assert chip.count(adapter[:symbols['recovery_profile_audio']])==1,'compiled adapter/planner/wave data altered'
 q=chip.index(adapter[:symbols['recovery_profile_audio']])
 a=symbols['recovery_profile_audio'];z=a+56
 assert adapter[a:a+8]==chip[q+a:q+a+8]==b'CDRPROA1'
 assert z<=symbols['mp'] and chip[q+z:q+symbols['mp']]==adapter[z:symbols['mp']], 'unexpected mutable gap'
 assert bytes(chip[q:q+a])==adapter[:a]""")
 ns={'__name__':'recovery_profile_frozen_verify','__file__':str(path)}
 exec(compile(s,str(path),'exec'),ns);ns['check'](out);return report(out)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('output',type=Path);v=a.parse_args();verify(v.output)
