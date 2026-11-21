"""Settlement guards for the end-to-end 2025 calculation."""

from pathlib import Path
import re
import subprocess
import tempfile
import unittest


def catala_scopes(scopes):
    """Run catala interpret on each scope of test_irs_2025.catala_en."""
    cirs = Path(__file__).resolve().parents[1] / "cirs"
    with tempfile.TemporaryDirectory() as directory:
        fixture = Path(directory) / "run.catala_en"
        fixture.write_text((cirs.parent / "tests" / "test_irs_2025.catala_en")
                           .read_text(encoding="utf-8"), encoding="utf-8")
        return [
            subprocess.run(
                ["catala", "interpret", "--whole-program", "-I", str(cirs), "-I", "tests",
                 "--scope", scope, str(fixture)],
                capture_output=True, text=True, timeout=60,
            )
            for scope in scopes
        ]


class SettlementGuards(unittest.TestCase):
    def test_success_paths_compute(self):
        """The complete calculation has no unresolved conflicts."""
        for result in catala_scopes(["TesteIRS2025"]):
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_refund_xor_payment(self):
        """Exactly one of a_pagar/reembolso is nonzero on each path."""
        results = catala_scopes(["TesteIRS2025"])
        self.assertEqual(len(results), 1)
        text = results[0].stdout
        pairs = re.findall(r"a_pagar: \$([\d.]+).*?reembolso: \$([\d.]+)", text, re.S)
        self.assertTrue(pairs, text)
        for paying, refund in pairs:
            self.assertTrue(float(paying) == 0 or float(refund) == 0,
                            f"both payable {paying} and refund {refund}")


if __name__ == "__main__":
    unittest.main()
