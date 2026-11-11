#!/usr/bin/env python3
"""No ROM/firmware: compile CIA probes and execute user-mode register tests."""
from pathlib import Path
import importlib.util,json,os,re,subprocess,sys,tempfile
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'tools'))
import recovery_profile_build as build
from recovery_profile_probe_test import test
with tempfile.TemporaryDirectory(prefix='recovery-profile-public-') as d:
 out=Path(d);src=out/'probe.s'
 src.write_text(' include "amiga_clock.s"\n'+build.instrumentation())
 subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-I'+str(P/'src'),'-L',str(out/'target.list'),'-o',str(out/'target.bin'),str(src)],check=True)
 symbols={name:int(addr,16) for addr,name in re.findall(r'^([0-9A-Fa-f]{8}) ([A-Za-z_][A-Za-z_0-9]*)$',(out/'target.list').read_text(),re.M)}
 (out/'target.symbols.json').write_text(json.dumps(symbols));test(out)
 # Transform sites must fail closed if upstream no longer matches.
 try:build.once('duplicated duplicated','duplicated','x')
 except AssertionError:pass
 else:raise AssertionError('ambiguous substitution accepted')
 assert 'move.w sr,-(sp)' not in build.instrumentation()
print('PASS: public profiler assembly and fail-closed source substitution, no private inputs.')
