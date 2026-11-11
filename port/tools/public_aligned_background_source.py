"""Prepare synthetic aligned-renderer assembly from public source only.

This module does not import unpublished target builders, inspect captures or build
from cartridge/firmware data. The caller supplies an existing output directory.
"""
from pathlib import Path
from recovery_play_background_build import prepare as prepare_background


def prepare(source, output):
    output = Path(output)
    source = prepare_background(source, output)
    device = output / 'recovery_play_background_device.s'
    text = device.read_text()
    substitutions = (
        (' bsr recovery_stage_background_draw', ' bsr recovery_aligned_background_draw'),
        (' include "recovery_stage_background_draw.s"', ' include "recovery_aligned_background_draw.s"'),
    )
    for old, _ in substitutions:
        if text.count(old) != 1:
            raise ValueError('expected exactly one background call and include')
    for old, new in substitutions:
        text = text.replace(old, new, 1)
    device.write_text(text)
    return source
