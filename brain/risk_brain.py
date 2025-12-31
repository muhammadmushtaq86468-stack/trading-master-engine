import pandas as pd


class RiskBrain:
    def __init__(
        self,
        candles: pd.DataFrame,
        direction: str,
        min_rr: float = 2.0,
        risk_buffer_pips: float = 0.0002
    ):
        self.candles = candles
        self.direction = direction  # "BUY" or "SELL"
        self.min_rr = min_rr
        self.risk_buffer = risk_buffer_pips

    def _last_swing_low(self):
        return self.candles["low"].rolling(5).min().iloc[-2]

    def _last_swing_high(self):
        return self.candles["high"].rolling(5).max().iloc[-2]

    def evaluate(self):
        if self.candles is None or len(self.candles) < 50:
            return {
                "allowed": False,
                "reason": "Not enough candles for risk evaluation"
            }

        last_close = self.candles["close"].iloc[-1]

        if self.direction == "BUY":
            stop_loss = self._last_swing_low() - self.risk_buffer
            risk = last_close - stop_loss

            if risk <= 0:
                return {"allowed": False, "reason": "Invalid BUY risk"}

            take_profit = last_close + (risk * self.min_rr)

        elif self.direction == "SELL":
            stop_loss = self._last_swing_high() + self.risk_buffer
            risk = stop_loss - last_close

            if risk <= 0:
                return {"allowed": False, "reason": "Invalid SELL risk"}

            take_profit = last_close - (risk * self.min_rr)

        else:
            return {
                "allowed": False,
                "reason": "Unknown trade direction"
            }

        rr = abs((take_profit - last_close) / risk)

        if rr < self.min_rr:
            return {
                "allowed": False,
                "reason": f"Risk/Reward too low ({rr:.2f})"
            }

        return {
            "allowed": True,
            "direction": self.direction,
            "entry": last_close,
            "stop_loss": round(stop_loss, 6),
            "take_profit": round(take_profit, 6),
            "rr": round(rr, 2)
        }
