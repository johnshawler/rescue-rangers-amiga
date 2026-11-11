#!/usr/bin/env python3
"""Unchanged independent pixel oracle/ABI/bounds suite over additive renderer."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
a=(root/'src/recovery_stage_background_draw.s').read_text();b=(root/'src/recovery_aligned_background_draw.s').read_text()
assert a[a.index('.byte:'):a.index('        lea 40(a2),a2')]==b[b.index('.byte:'):b.index('        bra.s .row_finished')]
p=Path(__file__).with_name('recovery_stage_background_test.py');s=p.read_text();a="assemble('recovery_stage_background_draw.s')";assert s.count(a)==1;s=s.replace(a,"assemble('recovery_aligned_background_draw.s')")
exec(compile(s,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
