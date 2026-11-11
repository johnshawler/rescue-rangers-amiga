#!/usr/bin/env python3
"""Invented-file contract tests. No cartridge, capture, compiler or emulator."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

TOOL = Path(__file__).absolute().parents[1] / 'tools/public_source_checkpoint.py'
spec = importlib.util.spec_from_file_location('source_contract', TOOL)
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


class SourceContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='public-source-contract-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'source'
        self.root.mkdir()
        self.files = {'src/invented.s': b'    rts\n', 'tools/invented.py': b'print(2 + 2)\n'}
        names = sorted([*self.files, contract.INVENTORY])
        self.files[contract.INVENTORY] = ('\n'.join(names) + '\n').encode('ascii')
        self.rows = []
        for name, data in sorted(self.files.items()):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            path.chmod(0o755 if name.startswith('tools/') else 0o644)
            self.rows.append(dict(path=name, size=len(data), sha256=hashlib.sha256(data).hexdigest(), executable=name.startswith('tools/')))
        self.manifest = dict(schema=contract.SCHEMA, files=self.rows)
        self.save()
        self.anchor = patch.object(contract, 'INVENTORY_SHA256', hashlib.sha256(self.files[contract.INVENTORY]).hexdigest())
        self.anchor.start()
        self.addCleanup(self.anchor.stop)

    def save(self):
        (self.root / contract.MANIFEST).write_text(json.dumps(self.manifest), encoding='utf-8')

    def reject(self, pattern):
        with self.assertRaisesRegex(contract.ContractError, pattern):
            contract.check(self.root, exact=True)

    def test_valid_check_and_fresh_restore(self):
        contract.check(self.root, exact=True)
        dest = self.base / 'restored'
        self.assertEqual(contract.restore(self.root, dest), 4)
        self.assertEqual(contract.check(dest, exact=True), self.manifest)
        for name in [*self.files, contract.MANIFEST]:
            self.assertEqual((self.root / name).read_bytes(), (dest / name).read_bytes())

    def test_check_does_not_write(self):
        before = {p.relative_to(self.root): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob('*') if p.is_file()}
        contract.check(self.root, exact=True)
        after = {p.relative_to(self.root): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_missing_manifest(self):
        (self.root / contract.MANIFEST).unlink()
        self.reject('missing')

    def test_empty_manifest(self):
        (self.root / contract.MANIFEST).write_bytes(b'')
        self.reject('JSON')

    def test_non_object_manifest(self):
        self.manifest = []
        self.save()
        self.reject('fields')

    def test_empty_file_list(self):
        self.manifest['files'] = []
        self.save()
        self.reject('empty')

    def test_duplicate_json_key(self):
        (self.root / contract.MANIFEST).write_text('{"schema": "x", "schema": "y", "files": []}')
        self.reject('duplicate JSON key')

    def test_unknown_schema(self):
        self.manifest['schema'] = 'different'
        self.save()
        self.reject('schema')

    def test_unknown_manifest_field(self):
        self.manifest['extra'] = 'invented'
        self.save()
        self.reject('fields')

    def test_invalid_entry_fields(self):
        self.rows[0]['extra'] = True
        self.save()
        self.reject('entry fields')

    def test_invalid_paths(self):
        for name in ('', '/absolute', '../outside', 'src/../outside', './src/a', 'src//a', 'src/', 'C:/x', 'src\\x', '.git/config', 'src/\x00x', 'src/space name', None):
            with self.subTest(name=name):
                self.manifest['files'] = copy.deepcopy(self.rows)
                self.manifest['files'][0]['path'] = name
                self.save()
                self.reject('invalid relative path')

    def test_duplicate_entry(self):
        self.rows.append(copy.deepcopy(self.rows[0]))
        self.save()
        self.reject('duplicate')

    def test_self_entry(self):
        self.rows[0]['path'] = contract.MANIFEST
        self.save()
        self.reject('self-referential')

    def test_unsorted_entries(self):
        self.rows.reverse()
        self.save()
        self.reject('sorted')

    def test_invalid_sizes(self):
        for size in (0, -1, True, '8', None):
            with self.subTest(size=size):
                self.rows[0]['size'] = size
                self.save()
                self.reject('size')

    def test_invalid_hashes(self):
        for value in ('', 'g' * 64, 'A' * 64, '0' * 63, None):
            with self.subTest(value=value):
                self.rows[0]['sha256'] = value
                self.save()
                self.reject('digest')

    def test_invalid_mode(self):
        self.rows[0]['executable'] = 1
        self.save()
        self.reject('executable flag')

    def test_changed_mode(self):
        (self.root / 'tools/invented.py').chmod(0o644)
        self.reject('mode')

    def test_missing_source(self):
        (self.root / 'src/invented.s').unlink()
        self.reject('missing')

    def test_changed_source_same_size(self):
        (self.root / 'src/invented.s').write_bytes(b'    nop\n')
        self.reject('changed')

    def test_empty_source(self):
        (self.root / 'src/invented.s').write_bytes(b'')
        self.reject('empty source')

    def test_missing_inventory(self):
        (self.root / contract.INVENTORY).unlink()
        self.reject('missing')

    def test_changed_inventory_even_if_manifest_rehashed(self):
        data = b'src/invented.s\n'
        (self.root / contract.INVENTORY).write_bytes(data)
        self.rows[0].update(size=len(data), sha256=hashlib.sha256(data).hexdigest())
        self.save()
        self.reject('inventory changed')

    def test_missing_closure_entry(self):
        self.rows.pop()
        self.save()
        self.reject('closure mismatch')

    def test_extra_closure_entry(self):
        row = copy.deepcopy(self.rows[-1])
        row['path'] = 'unexpected.py'
        self.rows.append(row)
        self.save()
        self.reject('closure mismatch')

    def test_extra_file_exact_check(self):
        (self.root / 'unexpected.txt').write_text('invented\n')
        contract.check(self.root)  # Non-exact check deliberately permits working outputs.
        self.reject('exact closure')
        dest = self.base / 'restored'
        contract.restore(self.root, dest)
        self.assertFalse((dest / 'unexpected.txt').exists())

    def test_exact_check_rejects_injected_directory_scan_errors(self):
        hidden = self.root / 'unlisted-directory'
        hidden.mkdir()
        (hidden / 'unlisted.txt').write_text('invented extra file\n')
        original = contract.os.scandir
        for error_type in (PermissionError, OSError):
            for denied in (self.root, hidden):
                with self.subTest(error=error_type.__name__, directory=denied.name):
                    def scan(path):
                        if Path(path) == denied:
                            raise error_type('injected directory scan failure')
                        return original(path)

                    with patch.object(contract.os, 'scandir', side_effect=scan):
                        self.reject('cannot traverse exact source closure')

    def test_exact_check_rejects_real_unreadable_extra_directory(self):
        hidden = self.root / 'unreadable-directory'
        hidden.mkdir()
        (hidden / 'unlisted.txt').write_text('invented extra file\n')
        hidden.chmod(0)
        try:
            try:
                with contract.os.scandir(hidden) as entries:
                    list(entries)
            except PermissionError:
                pass  # This account/filesystem enforces the unreadable mode.
            else:
                self.skipTest('directory permissions not enforced for this account/filesystem')
            self.reject('cannot traverse exact source closure')
        finally:
            hidden.chmod(0o755)

    def test_regular_git_directory_is_not_source(self):
        (self.root / '.git').mkdir()
        (self.root / '.git/config').write_text('invented local metadata\n')
        contract.check(self.root, exact=True)

    def test_symlink_file_internal(self):
        path = self.root / 'src/invented.s'
        path.unlink()
        path.symlink_to(self.root / 'tools/invented.py')
        self.reject('symlink')

    def test_symlink_file_external(self):
        outside = self.base / 'outside'
        outside.write_bytes(self.files['src/invented.s'])
        path = self.root / 'src/invented.s'
        path.unlink()
        path.symlink_to(outside)
        self.reject('symlink')

    def test_dangling_symlink(self):
        path = self.root / 'src/invented.s'
        path.unlink()
        path.symlink_to(self.base / 'absent')
        self.reject('symlink')

    def test_symlink_manifest(self):
        path = self.root / contract.MANIFEST
        outside = self.base / 'manifest'
        path.rename(outside)
        path.symlink_to(outside)
        self.reject('symlink')

    def test_symlink_source_parent(self):
        directory = self.root / 'src'
        directory.rename(self.base / 'actual-src')
        directory.symlink_to(self.base / 'actual-src', target_is_directory=True)
        self.reject('symlink')

    def test_symlink_root(self):
        alias = self.base / 'alias'
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(contract.ContractError, 'symlink'):
            contract.check(alias)

    def test_symlink_extra_directory(self):
        (self.root / 'extra').symlink_to(self.base, target_is_directory=True)
        self.reject('symlink')

    def test_nonregular_source(self):
        path = self.root / 'src/invented.s'
        path.unlink()
        path.mkdir()
        self.reject('not a regular')

    def test_restore_rejects_existing_destination_without_changes(self):
        dest = self.base / 'exists'
        dest.mkdir()
        sentinel = dest / 'keep.txt'
        sentinel.write_bytes(b'keep\n')
        with self.assertRaisesRegex(contract.ContractError, 'must not exist'):
            contract.restore(self.root, dest)
        self.assertEqual(sentinel.read_bytes(), b'keep\n')

    def test_restore_rejects_symlink_destination(self):
        dest = self.base / 'link'
        dest.symlink_to(self.base / 'absent')
        with self.assertRaisesRegex(contract.ContractError, 'must not exist'):
            contract.restore(self.root, dest)

    def test_restore_rejects_symlink_destination_parent(self):
        alias = self.base / 'alias'
        alias.symlink_to(self.base, target_is_directory=True)
        with self.assertRaisesRegex(contract.ContractError, 'symlink'):
            contract.restore(self.root, alias / 'restored')

    def test_restore_rejects_nested_destination(self):
        with self.assertRaisesRegex(contract.ContractError, 'outside'):
            contract.restore(self.root, self.root / 'nested')

    def test_restore_validation_failure_writes_nothing(self):
        (self.root / 'src/invented.s').write_bytes(b'')
        dest = self.base / 'restored'
        with self.assertRaises(contract.ContractError):
            contract.restore(self.root, dest)
        self.assertFalse(dest.exists())
        self.assertEqual(list(self.base.glob('.public-source-restore-*')), [])

    def test_restore_copy_failure_cleans_staging(self):
        dest = self.base / 'restored'
        original = contract.file_bytes
        reads = 0

        def changed_during_copy(root, name):
            nonlocal reads
            if name == 'src/invented.s':
                reads += 1
                if reads > 1:
                    return b'changed while copying\n'
            return original(root, name)

        with patch.object(contract, 'file_bytes', side_effect=changed_during_copy):
            with self.assertRaisesRegex(contract.ContractError, 'during restore'):
                contract.restore(self.root, dest)
        self.assertFalse(dest.exists())
        self.assertEqual(list(self.base.glob('.public-source-restore-*')), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
