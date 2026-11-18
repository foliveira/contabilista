"""Negative Catala checks (run separately from clerk test).

Run: python -m unittest discover -s tests -p 'test_*_guards.py'
Requires Catala 1.3.0 on PATH. Temporary fixtures never enter the clerk suite.
"""

from pathlib import Path
import subprocess
import tempfile
import unittest


class EnglobamentoGuards(unittest.TestCase):
    def test_input_contract(self):
        base = {
            "ano": "2025",
            "apenas_residentes": "true",
            "apenas_regime_geral_a_h": "true",
            "rendimentos_isentos_com_englobamento": "$0",
            "titulares": "[]",
        }
        cases = [
            ("valid empty", {}, True),
            ("unsupported year with empty list", {"ano": "2026"}, False),
            ("non-resident", {"apenas_residentes": "false"}, False),
            ("special regime", {"apenas_regime_geral_a_h": "false"}, False),
            ("exempt income", {"rendimentos_isentos_com_englobamento": "$1"}, False),
        ]
        for category in ("a", "h"):
            a, h = ("-$0.01", "$0") if category == "a" else ("$0", "-$0.01")
            cases.append((f"negative net {category}", {
                "titulares": "[Art_022.RendimentosTitular { "
                f"-- rendimento_liquido_a: {a} -- rendimento_liquido_h: {h} }}]"
            }, False))

        cirs = Path(__file__).resolve().parents[1] / "cirs"
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "guards.catala_en"
            for name, overrides, valid in cases:
                with self.subTest(name=name):
                    fields = base | overrides
                    fixture.write_text(
                        "> Using Art_022\n\n```catala\n"
                        "declaration scope Check:\n"
                        "  output resultado content Art_022.Englobamento\n"
                        "scope Check:\n"
                        "  definition resultado equals output of Art_022.Englobamento with {\n"
                        + "\n".join(f"    -- {key}: {value}" for key, value in fields.items())
                        + "\n  }\n```\n", encoding="utf-8"
                    )
                    result = subprocess.run(
                        ["catala", "interpret", "-I", str(cirs), "--scope=Check", str(fixture)],
                        capture_output=True, text=True, timeout=30,
                    )
                    diagnostic = result.stdout + result.stderr
                    self.assertEqual(result.returncode == 0, valid, diagnostic)
                    if not valid:
                        # A parser/type/import error is not a successful rejection.
                        self.assertIn("assertion", diagnostic.lower(), diagnostic)


if __name__ == "__main__":
    unittest.main()
