"""Independent exact arithmetic plus direct Catala comparison for art. 70.

This validates the explicitly chosen literal reading, NOT AT behavior.
"""
from fractions import Fraction as F
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


def literal(gross, deductions, dependent):
    expenses = F(0 if dependent else 250)
    reference = F(12180)
    l = reference - expenses / F('.125') * F('3.60') + F(8059) / F('3.60')
    gross, deductions = F(str(gross)), F(str(deductions))
    if gross <= reference and gross > l:
        raise ValueError('literal overlap')
    if gross <= reference:
        value = reference - deductions - expenses / F('.125')
    elif gross <= l:
        value = reference - F('2.60') * (gross - reference) - deductions - expenses / F('.125')
    else:
        value = l - 8059 - F('1.35') * (gross - l) - deductions
    value = max(F(0), min(gross - deductions, value))
    cents = value * 100
    rounded = (2 * cents.numerator + cents.denominator) // (2 * cents.denominator)
    return l, rounded


class LiteralReference(unittest.TestCase):
    def test_concrete_literal_case(self):
        l, cents = literal(13000, '4462.15', True)
        self.assertEqual(l, F(259535, 18))
        self.assertEqual(cents, 558585)  # L is NOT the abatement.
        self.assertEqual(literal(13000, '4462.15', False)[1], 0)
        with self.assertRaises(ValueError):
            literal(12180, '4462.15', False)

    def test_catala_matches_exact_literal_arithmetic(self):
        root = Path(__file__).resolve().parents[1]
        cases = [(7000, '4462.15', False), (13000, '4462.15', False),
                 (13000, '4462.15', True), (14418.61, '4462.15', True),
                 (14418.62, '4462.15', True), (16093, '4462.15', True)]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'reference.catala_en'
            for gross, deductions, dependent in cases:
                with self.subTest(gross=gross, dependent=dependent):
                    l, cents = literal(gross, deductions, dependent)
                    path.write_text(f'''> Using Art_070
```catala
declaration scope Check:
  output r content Art_070.MinimoExistencia
scope Check:
  definition r equals output of Art_070.MinimoExistencia with {{
    -- ano: 2025 -- numero_sujeitos_passivos: 1
    -- rendimentos_brutos_declaracao: ${gross} -- rendimentos_taxas_liberatorias: $0
    -- rendimento_bruto: ${gross} -- deducoes_especificas: ${deductions}
    -- dependente: {str(dependent).lower()} -- rendimento_predominante_elegivel: true
  }}
  assertion (r.l = {l.numerator}.0 / {l.denominator}.0)
  assertion (r.abatimento = ${cents // 100}.{cents % 100:02})
```
''', encoding='utf-8')
                    run = subprocess.run(['catala', 'interpret', '-I', str(root / 'cirs'),
                                          '--scope=Check', str(path)],
                                         capture_output=True, text=True, timeout=30)
                    self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == '__main__':
    unittest.main()
