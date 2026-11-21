"""€12,180 calculation through settlement: literal overlap fails closed."""

from pathlib import Path
import subprocess
import tempfile
import unittest


class LiteralMinimoGuards(unittest.TestCase):
    def test_reference_income_through_settlement(self):
        cirs = Path(__file__).resolve().parents[1] / "cirs"
        source = '''> Using Art_025
> Using Art_022
> Using Art_070
> Using Art_068
> Using Art_078_b
> Using Art_078_c
> Using Art_078_d
> Using Art_078

```catala
declaration scope Check:
  internal trabalho content Art_025.DeducaoTrabalho
  internal englobamento content Art_022.Englobamento
  internal minimo content Art_070.MinimoExistencia
  internal geral content Art_068.TaxasGerais
  internal despesas content Art_078_b.DespesasGerais
  internal saude content Art_078_c.Saude
  internal educacao content Art_078_d.Educacao
  output liquidacao content Art_078.Liquidacao
scope Check:
  definition trabalho equals output of Art_025.DeducaoTrabalho with {
    -- ano: 2025 -- rendimento_bruto: $12,180
    -- contribuicoes_obrigatorias: $1,339.80 -- indemnizacoes_elegiveis: $0
    -- quotizacoes_sindicais_elegiveis: $0 -- quotizacoes_ordens_elegiveis: $0
  }
  definition englobamento equals output of Art_022.Englobamento with {
    -- ano: 2025 -- apenas_residentes: true -- apenas_regime_geral_a_h: true
    -- rendimentos_isentos_com_englobamento: $0
    -- titulares: [Art_022.RendimentosTitular {
      -- rendimento_liquido_a: trabalho.rendimento_liquido -- rendimento_liquido_h: $0 }]
  }
  definition minimo equals output of Art_070.MinimoExistencia with {
    -- ano: 2025 -- numero_sujeitos_passivos: 1
    -- rendimentos_brutos_declaracao: $12,180 -- rendimentos_taxas_liberatorias: $0
    -- rendimento_bruto: $12,180 -- deducoes_especificas: trabalho.deducao
    -- dependente: false -- rendimento_predominante_elegivel: ELIGIBLE
  }
  definition geral equals output of Art_068.TaxasGerais with {
    -- ano: 2025 -- rendimento_coletavel: englobamento.rendimento_coletavel - minimo.abatimento
  }
  definition despesas equals output of Art_078_b.DespesasGerais with {
    -- ano: 2025 -- despesas_elegiveis: $1,000 -- numero_sujeitos_passivos: 1 -- monoparental: false
  }
  definition saude equals output of Art_078_c.Saude with {
    -- ano: 2025 -- despesas_elegiveis_liquidas: $100 -- separada: false
  }
  definition educacao equals output of Art_078_d.Educacao with {
    -- ano: 2025 -- despesas_elegiveis: $100 -- rendas_estudante_elegiveis: $0
    -- separada: false -- apenas_regime_cirs: true
  }
  definition liquidacao equals output of Art_078.Liquidacao with {
    -- ano: 2025 -- residente: true -- apenas_creditos_implementados: true
    -- conjunta: false -- separada: false -- dependentes: 0
    -- rendimento_coletavel: englobamento.rendimento_coletavel - minimo.abatimento
    -- coleta: geral.imposto -- descendentes_ascendentes: $0
    -- gerais: despesas.deducao -- saude: saude.deducao -- educacao: educacao.deducao
    -- imoveis: $0 -- fatura: $0 -- retencoes: $700 -- pagamentos_por_conta: $0
  }
  assertion (englobamento.rendimento_coletavel = $7,717.85)
  # Control only: disabling eligibility is NOT a workaround for real A income.
  assertion (liquidacao.imposto_devido = $669.73)
  assertion (liquidacao.reembolso = $30.27)
```
'''
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "reference.catala_en"
            for eligible in ("false", "true"):
                with self.subTest(eligible=eligible):
                    fixture.write_text(source.replace("ELIGIBLE", eligible), encoding="utf-8")
                    result = subprocess.run(
                        ["catala", "interpret", "--whole-program", "-I", str(cirs), "--scope=Check", str(fixture)],
                        capture_output=True, text=True, timeout=30,
                    )
                    diagnostic = result.stdout + result.stderr
                    if eligible == "false":
                        self.assertEqual(result.returncode, 0, diagnostic)
                    else:
                        self.assertNotEqual(result.returncode, 0, diagnostic)
                        self.assertIn("conflict between multiple valid consequences", diagnostic.lower(), diagnostic)
                        self.assertIn("art_070.catala_en", diagnostic, diagnostic)


if __name__ == "__main__":
    unittest.main()
