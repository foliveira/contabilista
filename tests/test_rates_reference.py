"""Independent Fraction oracle for the deliberately literal art.68/69 rules.

This is not the AT parcela table or a simulator oracle. Boundary and rounding
cases are intentionally retained even when the arithmetic is discontinuous.
"""
from fractions import Fraction as F
from pathlib import Path
import subprocess
import tempfile
import unittest

LIMITS = [8059, 12160, 17233, 22306, 28400, 41629, 44987, 83696]
NORMAL = [F('0.125'), F('.16'), F('.215'), F('.244'), F('.314'),
          F('.349'), F('.431'), F('.446'), F('.48')]
AVERAGE = [F('.125'), F('.13680'), F('.15982'), F('.17897'), F('.20794'),
           F('.25277'), F('.26607'), F('.34929')]


def round_cents(euros):
    cents = euros * 100
    return (2 * cents.numerator + cents.denominator) // (2 * cents.denominator)


def general(cents):
    income = F(cents, 100)
    if income <= LIMITS[0]:
        exact = income * NORMAL[0]
    else:
        index = max(i for i, limit in enumerate(LIMITS) if income >= limit)
        exact = LIMITS[index] * AVERAGE[index] + (income - LIMITS[index]) * NORMAL[index + 1]
    return round_cents(exact)


def joint(cents):
    # Existing scope rounds quotient, rounds tax, then doubles.
    return 2 * general((cents + 1) // 2)


def solidarity(cents, joint_filing=False):
    income = F(cents, 100) / (2 if joint_filing else 1)
    exact = max(F(0), min(income, F(250000)) - 80000) * F('.025')
    exact += max(F(0), income - 250000) * F('.05')
    return round_cents(exact * (2 if joint_filing else 1))


def money(cents):
    return f'${cents // 100}.{cents % 100:02}'


class RatesReference(unittest.TestCase):
    def test_boundary_and_rounding_matrix(self):
        incomes = {0, 1, 7, 805900, 805901, 805902, 805903, 50000000}
        for limit in LIMITS + [80000, 250000]:
            for offset in (-1, 0, 1):
                incomes.add(limit * 100 + offset)
                incomes.add(limit * 200 + offset)
        # Every assertion is generated from an independent exact rational oracle.
        code = '> Using Art_068\n> Using Art_069\n> Using Art_068_a\n```catala\n'
        code += 'declaration scope Check:\n  output ok condition\nscope Check:\n  definition ok equals true\n'
        for income in sorted(incomes):
            code += (f'  assertion ((output of Art_068.TaxasGerais with {{ -- ano: 2025 '
                     f'-- rendimento_coletavel: {money(income)} }}).imposto = {money(general(income))})\n')
            code += (f'  assertion ((output of Art_069.TributacaoConjunta with {{ -- ano: 2025 '
                     f'-- opcao_tributacao_conjunta: true -- rendimento_coletavel: {money(income)} '
                     f'}}).imposto = {money(joint(income))})\n')
            for jointly in (False, True):
                code += (f'  assertion ((output of Art_068_a.TaxaSolidariedade with {{ -- ano: 2025 '
                         f'-- tributacao_conjunta: {str(jointly).lower()} '
                         f'-- rendimento_coletavel: {money(income)} }}).imposto = '
                         f'{money(solidarity(income, jointly))})\n')
        code += '```\n'
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / 'reference.catala_en'
            fixture.write_text(code, encoding='utf-8')
            result = subprocess.run(['catala', 'interpret', '-I', str(root / 'cirs'),
                                     '--scope=Check', str(fixture)],
                                    capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_known_discontinuity_is_not_hidden(self):
        self.assertGreater(general(4498699), general(4498700))
        self.assertEqual(joint(7), 2)  # Documented provisional double rounding.


if __name__ == '__main__':
    unittest.main()
