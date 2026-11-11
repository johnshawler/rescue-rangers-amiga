"""Source-preparation contracts using public source and invented text only."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

PORT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(PORT / 'tools'))
import public_aligned_background_source as aligned
from recovery_live_gameplay_source import integrated_source
from recovery_play_background_build import prepare as baseline_prepare


class SourcePreparationTests(unittest.TestCase):
    def test_public_source_has_only_two_device_substitutions(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            original = integrated_source()
            expected_source = baseline_prepare(original, out)
            device = out / 'recovery_play_background_device.s'
            before = device.read_text()
            expected_device = before.replace(' bsr recovery_stage_background_draw', ' bsr recovery_aligned_background_draw', 1).replace(' include "recovery_stage_background_draw.s"', ' include "recovery_aligned_background_draw.s"', 1)
            self.assertEqual(aligned.prepare(original, out), expected_source)
            self.assertEqual(device.read_text(), expected_device)
            self.assertEqual(sorted(p.name for p in out.iterdir()), [device.name])
            self.assertEqual(aligned.prepare(original, out), expected_source)
            self.assertEqual(device.read_text(), expected_device)

    def test_missing_or_repeated_substitutions_fail_without_partial_replacement(self):
        call = ' bsr recovery_stage_background_draw'
        include = ' include "recovery_stage_background_draw.s"'
        for calls, includes in ((0, 1), (2, 1), (1, 0), (1, 2), (0, 0)):
            with self.subTest(calls=calls, includes=includes), tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp)
                device = out / 'recovery_play_background_device.s'
                invented = '\n'.join([call] * calls + [include] * includes) + '\n'

                def prepare_invented(source, output):
                    device.write_text(invented)
                    return source

                with patch.object(aligned, 'prepare_background', side_effect=prepare_invented):
                    with self.assertRaisesRegex(ValueError, 'exactly one'):
                        aligned.prepare('invented assembly', out)
                self.assertEqual(device.read_text(), invented)

    def test_helper_has_no_new_target_builder_import(self):
        import ast
        tree = ast.parse((PORT / 'tools/public_aligned_background_source.py').read_text())
        imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        self.assertEqual(imports, ['pathlib', 'recovery_play_background_build'])
        self.assertFalse(any(isinstance(node, ast.Import) for node in ast.walk(tree)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
