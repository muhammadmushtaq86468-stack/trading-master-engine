import requests
import pandas as pd
from datetime import datetime, timezone

class CandleReader:
    def __init__(self, pair="EURUSD=X", timeframe="30m", candles_limit=200):
        self.pair = pair
        self.timeframe = timeframe
        self.candles_limit = candles_limit

    def _build_url(self):
        return (
            "https://query2.finance.yahoo.com/v8/finance/chart/"
            f"{self.pair}"
            f"?interval={self.timeframe}&range=60d"
        )

    def get_candles(self):
        r = requests.get(
            self._build_url(),
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        data = r.json()

        if "chart" not in data or data["chart"]["error"] is not None:
            return pd.DataFrame(columns=["time", "open", "high", "low", "close"])

        result = data["chart"]["result"][0]
        timestamps = result["timestamp"]
        indicators = result["indicators"]["quote"][0]

        df = pd.DataFrame({
            "time": [datetime.fromtimestamp(t, tz=timezone.utc) for t in timestamps],
            "open": indicators["open"],
            "high": indicators["high"],
            "low": indicators["low"],
            "close": indicators["close"]
        })

        df = df.dropna()
        df = df.sort_values("time")
        df = df.tail(self.candles_limit).reset_index(drop=True)

        return df


if __name__ == "__main__":
    reader = CandleReader(pair="EURUSD=X", timeframe="30m", candles_limit=50)
    candles = reader.get_candles()

    if candles.empty:
        print("NO DATA")
    else:
        print(candles.tail())
