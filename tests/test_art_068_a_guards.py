"""Article 68-A contract checks; run with the README's unittest command."""

from pathlib import Path
import subprocess
import tempfile
import unittest


class TaxaSolidariedadeGuards(unittest.TestCase):
    def test_input_contract(self):
        cases = [
            ("valid zero", "2025", "$0", True),
            ("valid positive", "2025", "$600,000", True),
            ("negative income", "2025", "-$0.01", False),
            ("unsupported year below threshold", "2026", "$0", False),
            ("unsupported year above threshold", "2024", "$600,000", False),
        ]
        cirs = Path(__file__).resolve().parents[1] / "cirs"
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "guards.catala_en"
            for joint in ("false", "true"):
                for name, year, income, valid in cases:
                    with self.subTest(name=name, joint=joint):
                        fixture.write_text(
                            "> Using Art_068_a\n\n```catala\n"
                            "declaration scope Check:\n"
                            "  output resultado content Art_068_a.TaxaSolidariedade\n"
                            "scope Check:\n"
                            "  definition resultado equals output of Art_068_a.TaxaSolidariedade with {\n"
                            f"    -- ano: {year}\n"
                            f"    -- rendimento_coletavel: {income}\n"
                            f"    -- tributacao_conjunta: {joint}\n"
                            "  }\n```\n", encoding="utf-8"
                        )
                        result = subprocess.run(
                            ["catala", "interpret", "-I", str(cirs), "--scope=Check", str(fixture)],
                            capture_output=True, text=True, timeout=30,
                        )
                        diagnostic = result.stdout + result.stderr
                        self.assertEqual(result.returncode == 0, valid, diagnostic)
                        if not valid:
                            # Missing year-indexed parameters may be evaluated
                            # before the year assertion. Neither parser nor type
                            # errors count as a successful contract rejection.
                            expected = "assertion" if year == "2025" else "assertion|no applicable rule"
                            self.assertRegex(diagnostic.lower(), expected, diagnostic)
                            self.assertIn("art_068_a.catala_en", diagnostic, diagnostic)


if __name__ == "__main__":
    unittest.main()
