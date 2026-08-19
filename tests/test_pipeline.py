import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from update_data import analyze, currency_rates, market_regime  # noqa: E402


class PipelineTest(unittest.TestCase):
    def frame(self, drift, volume):
        rng = np.random.default_rng(7 + int(volume))
        index = pd.bdate_range(end=pd.Timestamp.today(), periods=300)
        close = 100 * np.cumprod(1 + rng.normal(drift, 0.01, len(index)))
        return pd.DataFrame({"Close": close, "High": close * 1.01, "Low": close * .99, "Volume": volume}, index=index)

    def test_v34_fields_and_regime(self):
        benchmark = self.frame(.0003, 10_000_000)
        row = analyze("Synthetic", "TEST", self.frame(.0007, 1_000_000), benchmark, "EUR")
        self.assertEqual(row["status"], "ok")
        for field in ("sma200", "relativeStrength20", "relativeStrength60", "avgTradedValue20",
                      "volumeRatio", "support20", "resistance20", "distanceToResistancePct",
                      "eligible", "interesting"):
            self.assertIn(field, row)
        self.assertIn(market_regime(benchmark)["label"], {"BULLISH", "NEUTRAL", "BEARISH"})

    def test_currency_rates_are_local_units_in_budget_currency(self):
        today = pd.Timestamp.now(tz="UTC").normalize()

        def loader(ticker):
            rates = {"SEKEUR=X": .087, "CHFEUR=X": 1.04, "NOKEUR=X": .086, "DKKEUR=X": .134}
            return pd.DataFrame({"Close": [rates[ticker]]}, index=[today])

        fx = currency_rates(loader)
        self.assertEqual(fx["EUR"]["rates"]["EUR"]["rate"], 1.0)
        self.assertEqual(fx["CAD"]["rates"]["CAD"]["rate"], 1.0)
        self.assertAlmostEqual(fx["EUR"]["rates"]["SEK"]["rate"], .087)
        self.assertEqual(fx["EUR"]["rates"]["SEK"]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
