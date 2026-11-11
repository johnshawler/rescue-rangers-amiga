"""Conservative linked-code budget using generated synthetic data only."""
import json
from pathlib import Path
import re
import sys
import unittest

PRG_BYTES = 128 * 1024
STRICT_CEILING = 3 * PRG_BYTES
BOOTBLOCK_BYTES = 1024


class BudgetError(ValueError):
    pass


def declared_zero_size(source, symbol):
    pattern = rf'^{symbol}:[ \t]*(?:\n[ \t]*)?dcb\.b[ \t]+([0-9]+),0[ \t]*$'
    matches = re.findall(pattern, source, re.M)
    if len(matches) != 1 or int(matches[0]) <= 0:
        raise BudgetError('expected one nonempty zero-buffer declaration: ' + symbol)
    return int(matches[0])


def account(image, symbols, source, device, resource, graphics, bootstrap):
    if not image or not 0 < len(bootstrap) <= BOOTBLOCK_BYTES:
        raise BudgetError('empty target or bootstrap outside its counted block')
    if any(len(data) != PRG_BYTES or any(data) for data in (resource, graphics)):
        raise BudgetError('expected generated 128 KiB zero fixtures')
    sizes = {
        'resource': len(resource),
        'startup_cartridge_chr': len(graphics),
        'journal': declared_zero_size(source, 'journal'),
        'capture': declared_zero_size(source, 'capture'),
        'startup_frame': declared_zero_size(device, 'startup_frame'),
    }
    spans = []
    for symbol, size in sizes.items():
        start = symbols.get(symbol)
        if type(start) is not int or start < 0 or start + size > len(image):
            raise BudgetError('missing or out-of-bounds span: ' + symbol)
        spans.append(dict(symbol=symbol, start=start, end_exclusive=start + size, bytes=size))
    spans.sort(key=lambda row: row['start'])
    for previous, following in zip(spans, spans[1:]):
        if previous['end_exclusive'] > following['start']:
            raise BudgetError('overlapping excluded spans')
    for span in spans:
        if any(image[span['start']:span['end_exclusive']]):
            raise BudgetError('excluded synthetic span is not zero: ' + span['symbol'])
    excluded = sum(span['bytes'] for span in spans)
    upper_bound = len(image) - excluded + BOOTBLOCK_BYTES
    if upper_bound >= STRICT_CEILING:
        raise BudgetError('conservative linked-code upper bound reaches strict ceiling')
    return dict(status='PASS', original_prg_bytes=PRG_BYTES,
                strict_ceiling_bytes=STRICT_CEILING, linked_payload_bytes=len(image),
                bootblock_bytes_counted=BOOTBLOCK_BYTES, bootstrap_file_bytes=len(bootstrap),
                excluded_nonexecutable_bytes=excluded, excluded_spans=spans,
                conservative_native_executable_upper_bound_bytes=upper_bound,
                scope='Counts all unexcluded linked bytes and a full bootblock, not Chip RAM allocation or an exact instruction-size total.')


def inspect(output):
    output = Path(output)
    return account((output / 'target.bin').read_bytes(),
                   json.loads((output / 'target.symbols.json').read_text()),
                   (output / 'synthetic.s').read_text(),
                   (output / 'recovery_play_background_device.s').read_text(),
                   (output / 'private-prg.bin').read_bytes(),
                   (output / 'startup-display-private-chr.bin').read_bytes(),
                   (output / 'synthetic-boot.bin').read_bytes())


class SyntheticBudgetTests(unittest.TestCase):
    def setUp(self):
        self.source = 'journal:\n dcb.b 4,0\ncapture:\n dcb.b 8,0\n'
        self.device = 'startup_frame: dcb.b 12,0\n'
        self.fixture = bytes(PRG_BYTES)
        self.symbols = dict(resource=32, startup_cartridge_chr=32 + PRG_BYTES,
                            journal=32 + 2 * PRG_BYTES,
                            capture=36 + 2 * PRG_BYTES,
                            startup_frame=44 + 2 * PRG_BYTES)
        self.image = bytearray(b'\x4e' * (64 + 2 * PRG_BYTES + 24))
        self.image[32:56 + 2 * PRG_BYTES] = bytes(24 + 2 * PRG_BYTES)
        self.bootstrap = bytes(78)

    def check(self):
        return account(self.image, self.symbols, self.source, self.device,
                       self.fixture, self.fixture, self.bootstrap)

    def test_conservative_positive(self):
        result = self.check()
        self.assertEqual(result['excluded_nonexecutable_bytes'], 2 * PRG_BYTES + 24)
        self.assertEqual(result['conservative_native_executable_upper_bound_bytes'], 1088)

    def test_every_unexcluded_byte_counts(self):
        before = self.check()['conservative_native_executable_upper_bound_bytes']
        self.image.extend(bytes(123))
        self.assertEqual(self.check()['conservative_native_executable_upper_bound_bytes'], before + 123)

    def test_exact_ceiling_rejected_and_one_below_passes(self):
        upper = self.check()['conservative_native_executable_upper_bound_bytes']
        self.image.extend(bytes(STRICT_CEILING - upper - 1))
        self.assertEqual(self.check()['conservative_native_executable_upper_bound_bytes'], STRICT_CEILING - 1)
        self.image.append(0)
        with self.assertRaisesRegex(BudgetError, 'strict ceiling'):
            self.check()

    def test_overlap_rejected(self):
        self.symbols['capture'] = self.symbols['journal'] + 2
        with self.assertRaisesRegex(BudgetError, 'overlapping'):
            self.check()

    def test_out_of_bounds_and_invalid_offsets_rejected(self):
        for offset in (-1, len(self.image), True, '32', None):
            with self.subTest(offset=offset):
                self.symbols['resource'] = offset
                with self.assertRaisesRegex(BudgetError, 'out-of-bounds'):
                    self.check()

    def test_missing_symbol_rejected(self):
        del self.symbols['journal']
        with self.assertRaisesRegex(BudgetError, 'missing'):
            self.check()

    def test_nonzero_excluded_bytes_rejected(self):
        self.image[self.symbols['journal']] = 1
        with self.assertRaisesRegex(BudgetError, 'not zero'):
            self.check()

    def test_nonzero_fixtures_rejected(self):
        self.fixture = b'\x01' + bytes(PRG_BYTES - 1)
        with self.assertRaisesRegex(BudgetError, 'zero fixtures'):
            self.check()

    def test_wrong_fixture_size_rejected(self):
        self.fixture = bytes(PRG_BYTES - 1)
        with self.assertRaisesRegex(BudgetError, 'zero fixtures'):
            self.check()

    def test_missing_repeated_empty_or_nonzero_declarations_rejected(self):
        original = self.source
        for source in ('', original + original, original.replace('4,0', '0,0'), original.replace('4,0', '4,1')):
            with self.subTest(source=source):
                self.source = source
                with self.assertRaisesRegex(BudgetError, 'zero-buffer declaration'):
                    self.check()

    def test_oversized_declared_span_rejected(self):
        self.source = self.source.replace('4,0', '999999,0')
        with self.assertRaisesRegex(BudgetError, 'out-of-bounds'):
            self.check()

    def test_bootstrap_bounds(self):
        self.bootstrap = bytes(BOOTBLOCK_BYTES)
        self.check()
        for size in (0, BOOTBLOCK_BYTES + 1):
            with self.subTest(size=size):
                self.bootstrap = bytes(size)
                with self.assertRaisesRegex(BudgetError, 'bootstrap'):
                    self.check()

    def test_empty_target_rejected(self):
        self.image = b''
        with self.assertRaisesRegex(BudgetError, 'empty target'):
            self.check()


if __name__ == '__main__':
    if len(sys.argv) == 2 and not sys.argv[1].startswith('-'):
        print(json.dumps(inspect(sys.argv[1]), indent=2))
    else:
        unittest.main(verbosity=2)
