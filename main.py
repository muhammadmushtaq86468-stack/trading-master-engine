import time
import json
from datetime import datetime, timezone

from data_feed.candle_reader import CandleReader
from brain.decision_engine import DecisionEngine


PAIRS = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "JPY=X",
    "AUDUSD": "AUDUSD=X",
    "USDCAD": "CAD=X",
    "USDCHF": "CHF=X"
}

TIMEFRAME = "30m"
CANDLES_LIMIT = 200
ANALYSIS_INTERVAL_SECONDS = 1
SIGNAL_FILE = "signals/signals.json"


def is_candle_closed(candles):
    if len(candles) < 2:
        return False

    last = candles.iloc[-1]
    prev = candles.iloc[-2]

    if last["open"] == last["high"] == last["low"] == last["close"]:
        return False

    if last["time"] == prev["time"]:
        return False

    return True


def analyze_pair(pair_name, symbol):
    reader = CandleReader(
        pair=symbol,
        timeframe=TIMEFRAME,
        candles_limit=CANDLES_LIMIT
    )

    candles = reader.get_candles()

    if candles.empty:
        return None

    if not is_candle_closed(candles):
        return None

    decision = DecisionEngine(candles).decide()
    decision["pair"] = pair_name
    decision["time"] = datetime.now(timezone.utc).isoformat()

    return decision


def save_signal(signal):
    try:
        with open(SIGNAL_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        data = []

    data.append(signal)

    with open(SIGNAL_FILE, "w") as f:
        json.dump(data, f, indent=2)


def main():
    print("LIVE TRADING MASTER SIGNAL ENGINE STARTED")
    print("Analyzing top 6 pairs every second...\n")

    while True:
        for pair_name, symbol in PAIRS.items():
            signal = analyze_pair(pair_name, symbol)

            if signal:
                save_signal(signal)
                print(signal)

        time.sleep(ANALYSIS_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
