import pandas as pd
import numpy as np


class MarketStructureAnalyzer:
    def __init__(self, candles: pd.DataFrame):
        self.candles = candles.copy()

        if len(self.candles) < 60:
            raise ValueError("Insufficient candles for structure analysis")

        self._prepare()

    def _prepare(self):
        self.candles = self.candles.sort_values("time").reset_index(drop=True)

        self.candles["range"] = self.candles["high"] - self.candles["low"]
        self.candles["body"] = abs(self.candles["close"] - self.candles["open"])

        self.candles["upper_wick"] = self.candles["high"] - self.candles[["open", "close"]].max(axis=1)
        self.candles["lower_wick"] = self.candles[["open", "close"]].min(axis=1) - self.candles["low"]

    def analyze(self):
        closed = self._get_closed_candles()

        trend = self._detect_trend(closed)
        swings = self._detect_swings(closed)
        structure = self._classify_structure(trend, swings)

        return {
            "trend": trend,
            "structure": structure,
            "last_high": swings["last_high"],
            "last_low": swings["last_low"],
            "higher_high": swings["higher_high"],
            "lower_low": swings["lower_low"]
        }

    def _get_closed_candles(self):
        last = self.candles.iloc[-1]
        prev = self.candles.iloc[-2]

        if (
            last["open"] == last["high"] == last["low"] == last["close"]
            or last["time"] == prev["time"]
        ):
            return self.candles.iloc[:-1]

        return self.candles

    def _detect_trend(self, df):
        highs = df["high"].values
        lows = df["low"].values

        hh = highs[-1] > highs[-5]
        hl = lows[-1] > lows[-5]

        lh = highs[-1] < highs[-5]
        ll = lows[-1] < lows[-5]

        if hh and hl:
            return "UP"
        if lh and ll:
            return "DOWN"
        return "RANGE"

    def _detect_swings(self, df):
        highs = df["high"].values
        lows = df["low"].values

        last_high = highs[-1]
        prev_high = highs[-5]

        last_low = lows[-1]
        prev_low = lows[-5]

        return {
            "last_high": float(last_high),
            "last_low": float(last_low),
            "higher_high": last_high > prev_high,
            "lower_low": last_low < prev_low
        }

    def _classify_structure(self, trend, swings):
        if trend == "UP" and swings["higher_high"]:
            return "BULLISH_CONTINUATION"

        if trend == "DOWN" and swings["lower_low"]:
            return "BEARISH_CONTINUATION"

        if trend == "RANGE":
            return "RANGE_BOUND"

        return "UNCLEAR"


# -------- MULTI-PAIR SAFE TEST --------

if __name__ == "__main__":
    from data_feed.candle_reader import CandleReader

    PAIRS = {
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "USDJPY": "JPY=X",
        "AUDUSD": "AUDUSD=X",
        "USDCAD": "CAD=X",
        "USDCHF": "CHF=X"
    }

    for name, symbol in PAIRS.items():
        reader = CandleReader(pair=symbol, timeframe="30m", candles_limit=120)
        candles = reader.get_candles()

        if candles.empty:
            print(f"{name}: NO DATA")
            continue

        analyzer = MarketStructureAnalyzer(candles)
        result = analyzer.analyze()

        print(name, result)
