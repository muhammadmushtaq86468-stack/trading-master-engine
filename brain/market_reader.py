import pandas as pd


class MarketReader:
    def __init__(self, candles: pd.DataFrame):
        self.candles = candles

    def analyze_market_health(self):
        if self.candles is None or len(self.candles) < 50:
            return {
                "status": "NO_TRADE",
                "reasons": ["Not enough candles"]
            }

        ranges = self.candles["high"] - self.candles["low"]
        avg_range = ranges.mean()

        if avg_range < 0.0002:
            return {
                "status": "NO_TRADE",
                "reasons": ["Low volatility"]
            }

        return {
            "status": "HEALTHY",
            "reasons": []
        }
