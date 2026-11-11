#!/usr/bin/env python3
"""Check/restore this public-source snapshot, not private runtime evidence."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile

MANIFEST = 'port/analysis/public_source_checkpoint.json'
INVENTORY = 'port/analysis/public_source_inventory.txt'
INVENTORY_SHA256 = '065d5577000d365a6b4cb5034b81db561484a3f844aaf9074e502734613f15cd'
SCHEMA = 'rescue-public-source-v1'


class ContractError(ValueError):
    pass


def relative_path(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9._/-]+', value):
        raise ContractError('invalid relative path')
    if any(p in ('', '.', '..', '.git') for p in value.split('/')):
        raise ContractError('invalid relative path: ' + value)
    return value


def absolute_directory(path):
    path = Path(os.path.abspath(path))
    for parent in reversed((path, *path.parents)):
        if parent.is_symlink():
            raise ContractError('symlink directory: ' + str(parent))
        if not parent.is_dir():
            raise ContractError('missing directory: ' + str(parent))
    return path


def file_bytes(root, name):
    path = root
    parts = relative_path(name).split('/')
    for index, part in enumerate(parts):
        path /= part
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError as exc:
            raise ContractError('missing file or parent: ' + name) from exc
        if stat.S_ISLNK(mode):
            raise ContractError('symlink file or parent: ' + name)
        wanted = stat.S_ISREG if index == len(parts) - 1 else stat.S_ISDIR
        if not wanted(mode):
            raise ContractError('not a regular file/directory: ' + name)
    return path.read_bytes()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def tree_files(root):
    def traversal_error(error):
        raise ContractError('cannot traverse exact source closure: ' + str(error)) from error

    result = set()
    for directory, folders, files in os.walk(root, followlinks=False, onerror=traversal_error):
        here = Path(directory)
        if here == root and '.git' in folders:
            if (here / '.git').is_symlink():
                raise ContractError('symlink Git metadata')
            folders.remove('.git')
        for folder in folders:
            if (here / folder).is_symlink():
                raise ContractError('symlink directory in exact closure')
        for name in files:
            path = (here / name).relative_to(root).as_posix()
            file_bytes(root, path)
            result.add(path)
    return result


def check(root, exact=False):
    root = absolute_directory(root)
    raw = file_bytes(root, MANIFEST)
    try:
        manifest = json.loads(raw, object_pairs_hook=unique_object)
    except (ValueError, UnicodeError) as exc:
        raise ContractError('invalid manifest JSON: ' + str(exc)) from exc
    if not isinstance(manifest, dict) or set(manifest) != {'schema', 'files'}:
        raise ContractError('invalid manifest fields')
    if manifest['schema'] != SCHEMA:
        raise ContractError('unknown manifest schema')
    rows = manifest['files']
    if not isinstance(rows, list) or not rows:
        raise ContractError('empty or invalid file list')
    indexed = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {'path', 'size', 'sha256', 'executable'}:
            raise ContractError('invalid file entry fields')
        name = relative_path(row['path'])
        if name == MANIFEST or name in indexed:
            raise ContractError('duplicate or self-referential manifest entry: ' + name)
        if type(row['size']) is not int or row['size'] <= 0:
            raise ContractError('empty or invalid entry size: ' + name)
        if not isinstance(row['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', row['sha256']):
            raise ContractError('invalid digest: ' + name)
        if type(row['executable']) is not bool:
            raise ContractError('invalid executable flag: ' + name)
        indexed[name] = row
    if list(indexed) != sorted(indexed):
        raise ContractError('file entries must be sorted')
    inventory = file_bytes(root, INVENTORY)
    if hashlib.sha256(inventory).hexdigest() != INVENTORY_SHA256:
        raise ContractError('source inventory changed')
    try:
        names = inventory.decode('ascii').splitlines()
    except UnicodeError as exc:
        raise ContractError('invalid source inventory') from exc
    for name in names:
        relative_path(name)
    if not names or names != sorted(set(names)) or MANIFEST in names or INVENTORY not in names:
        raise ContractError('invalid source inventory closure')
    if set(indexed) != set(names):
        raise ContractError('manifest/inventory closure mismatch')
    for name, row in indexed.items():
        data = file_bytes(root, name)
        if len(data) != row['size'] or hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ContractError('changed or empty source: ' + name)
        executable = bool((root / name).stat().st_mode & 0o111)
        if executable != row['executable']:
            raise ContractError('changed executable mode: ' + name)
    if exact and tree_files(root) != set(names) | {MANIFEST}:
        raise ContractError('unexpected or missing files in exact closure')
    return manifest


def restore(root, destination):
    root = absolute_directory(root)
    manifest = check(root)
    destination = Path(os.path.abspath(destination))
    parent = absolute_directory(destination.parent)
    if destination.exists() or destination.is_symlink():
        raise ContractError('destination must not exist')
    if destination == root or root in destination.parents:
        raise ContractError('destination must be outside the source tree')
    staging = Path(tempfile.mkdtemp(prefix='.public-source-restore-', dir=parent))
    try:
        for row in manifest['files']:
            data = file_bytes(root, row['path'])
            if len(data) != row['size'] or hashlib.sha256(data).hexdigest() != row['sha256']:
                raise ContractError('source changed during restore: ' + row['path'])
            target = staging / row['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            target.chmod(0o755 if row['executable'] else 0o644)
        (staging / MANIFEST).write_bytes(file_bytes(root, MANIFEST))
        check(staging, exact=True)
        if destination.exists() or destination.is_symlink():
            raise ContractError('destination appeared during restore')
        staging.rename(destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return len(manifest['files']) + 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    verify = commands.add_parser('check')
    verify.add_argument('--root', type=Path, default=Path(__file__).absolute().parents[2])
    verify.add_argument('--exact', action='store_true', help='reject extra files, except a top-level .git directory')
    copy = commands.add_parser('restore')
    copy.add_argument('destination', type=Path, help='new directory with an existing non-symlink parent')
    copy.add_argument('--root', type=Path, default=Path(__file__).absolute().parents[2])
    args = parser.parse_args()
    try:
        count = len(check(args.root, args.exact)['files']) + 1 if args.command == 'check' else restore(args.root, args.destination)
    except (ContractError, OSError) as exc:
        parser.exit(1, 'FAIL public source contract: ' + str(exc) + '\n')
    print(f'PASS public source {args.command}: {count} files; no private runtime evidence checked')


if __name__ == '__main__':
    main()
