"""Article 69 contract checks; run with the README's unittest command."""

from pathlib import Path
import subprocess
import tempfile
import unittest


class TributacaoConjuntaGuards(unittest.TestCase):
    def test_input_contract(self):
        base = {
            "ano": "2025",
            "opcao_tributacao_conjunta": "true",
            "rendimento_coletavel": "$0",
        }
        cases = [
            ("valid zero", {}, True),
            ("valid positive", {"rendimento_coletavel": "$50,000"}, True),
            ("unsupported year at zero", {"ano": "2026"}, False),
            ("unsupported year at positive income", {
                "ano": "2024", "rendimento_coletavel": "$50,000"
            }, False),
            ("no valid joint option", {"opcao_tributacao_conjunta": "false"}, False),
            ("negative odd-cent income", {
                "rendimento_coletavel": "-$0.01"
            }, False),
        ]
        cirs = Path(__file__).resolve().parents[1] / "cirs"
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "guards.catala_en"
            for name, overrides, valid in cases:
                with self.subTest(name=name):
                    fields = base | overrides
                    fixture.write_text(
                        "> Using Art_069\n\n```catala\n"
                        "declaration scope Check:\n"
                        "  output resultado content Art_069.TributacaoConjunta\n"
                        "scope Check:\n"
                        "  definition resultado equals output of Art_069.TributacaoConjunta with {\n"
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
                        if fields["ano"] != "2025":
                            # The nested art. 68 call is evaluated before the
                            # outer assertion and has no table for other years.
                            self.assertIn("no applicable rule", diagnostic.lower(), diagnostic)
                            self.assertIn("art_068.catala_en", diagnostic, diagnostic)
                        else:
                            self.assertIn("assertion", diagnostic.lower(), diagnostic)


if __name__ == "__main__":
    unittest.main()
