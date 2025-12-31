from brain.market_reader import MarketReader
from brain.structure_brain import MarketStructureAnalyzer
from brain.risk_brain import RiskBrain


class DecisionEngine:
    def __init__(
        self,
        candles,
        min_rr: float = 2.0
    ):
        self.candles = candles
        self.min_rr = min_rr

    def decide(self):
        if self.candles is None or len(self.candles) < 50:
            return {
                "signal": "NO_TRADE",
                "reason": "Insufficient candle data"
            }

        health = MarketReader(self.candles).analyze_market_health()
        if health["status"] != "HEALTHY":
            return {
                "signal": "NO_TRADE",
                "reason": health.get("reasons", [])
            }

        structure = MarketStructureAnalyzer(self.candles).analyze()
        direction = structure.get("direction")

        if direction not in ("BUY", "SELL"):
            return {
                "signal": "NO_TRADE",
                "reason": "No clear market direction"
            }

        risk = RiskBrain(
            candles=self.candles,
            direction=direction,
            min_rr=self.min_rr
        ).evaluate()

        if not risk.get("allowed"):
            return {
                "signal": "NO_TRADE",
                "reason": risk.get("reason")
            }

        return {
            "signal": direction,
            "entry": risk["entry"],
            "stop_loss": risk["stop_loss"],
            "take_profit": risk["take_profit"],
            "rr": risk["rr"]
        }
