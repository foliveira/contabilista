"""Contract checks for the public composition (never bypass unsupported facts)."""
import copy
from pathlib import Path
import subprocess
import tempfile
import unittest
from irs_fixtures import case, holder, render


class DeclaracaoGuards(unittest.TestCase):
    def test_contract(self):
        base = case('base', [holder(20000)])
        cases = [({}, True), ({'ano': 2026}, False), ({'residente': False}, False),
                 ({'apenas_regime_geral_a_h': False}, False),
                 ({'apenas_creditos_implementados': False}, False),
                 ({'titulares_integrais': False}, False),
                 ({'conjunta': True}, False),  # Missing spouse, including zero-income spouse.
                 ({'titulares': []}, False),
                 ({'titulares': [holder(20000), holder(20000)]}, False),
                 ({'conjunta': True, 'separada': True, 'titulares': [holder(20000), holder()]}, False),
                 ({'conjunta': True, 'elegivel_conjunta': False,
                   'titulares': [holder(20000), holder()]}, False),
                 ({'monoparental': True}, False),
                 ({'monoparental': True, 'dependentes': [{'idade': 10, 'partilhado': False}]}, True),
                 ({'titulares': [holder(20000), holder(1000, dependent=True)]}, False),
                 ({'separada': True, 'dependentes': [{'idade': 10, 'partilhado': False}]}, False),
                 ({'separada': True, 'ascendentes': 1}, False),
                 ({'titulares': [holder(-1)]}, False),
                 ({'titulares': [holder(h=20000, pensoes_elegiveis=False)]}, False),
                 ({'titulares': [holder(12180)]}, False),  # Literal conflict remains visible.
                 ({'retencoes': -1}, False), ({'pagamentos_por_conta': -1}, False)]
        for expense in ('gerais', 'saude', 'educacao', 'rendas_estudante', 'rendas', 'juros',
                        'iva_servicos', 'iva_transportes', 'iva_medicamentos_veterinarios',
                        'iva_publicacoes', 'iva_desporto'):
            cases.append(({'despesas': {expense: -1}}, False))
        cases.append(({'despesas': {'rendas': 1000, 'juros': 1000}}, False))
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'contract.catala_en'
            for overrides, valid in cases:
                with self.subTest(overrides=overrides):
                    c = copy.deepcopy(base) | overrides
                    path.write_text('> Using Irs_2025\n> Using Art_078_a\n' + render(c), encoding='utf-8')
                    r = subprocess.run(['catala', 'interpret', '-I', str(root / 'cirs'),
                                        '--scope=Check', str(path)],
                                       capture_output=True, text=True, timeout=30)
                    diagnostic = r.stdout + r.stderr
                    self.assertEqual(r.returncode == 0, valid, diagnostic)
                    if not valid:
                        self.assertRegex(diagnostic.lower(), 'assertion|no applicable rule|conflict')


if __name__ == '__main__':
    unittest.main()
