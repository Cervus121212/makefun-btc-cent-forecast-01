#!/usr/bin/env python3
"""btc-cent-forecast-01 entry: 4-hour-ahead BTC price forecast.

Model (v1): short-horizon mean reversion toward the 6-hour median.
    forecast = last_close + 0.5 * (median(last 360 closes) - last_close)

Why: on the practice recording (2026-11-07..11, cbBTC/USDC 1-minute closes)
the 4-hour-ahead move of BTC reverts toward the recent local level instead
of continuing: linear-trend extrapolation and EMA momentum both scored far
worse than persistence, while pulling halfway toward the 6-hour median beat
persistence on every backtest sample -- the 5 real practice cases
p00..p04 (targets taken from the next case's checkpoint close),
72 four-hour-spaced pseudo-cases, and 138 two-hour-spaced pseudo-cases
(see README.md for the numbers). The weight 0.5 sits on the plateau of the
calibration curve (0.5-0.6 best; 0.7+ degrades on all samples), and the
model carries no fixed drift, so it makes no directional bet on the final
window's regime. The reversion move is capped at +/-$1,000, a bound that
never binds on any backtest case (largest in-sample move is under it) and
only guards the unseen final window against a flash move dragging the
forecast halfway toward a stale level.

Deterministic, stdlib only, O(n log n) on 4,320 prices, well under the
8-second cap. Reads every <id>.in in $MAKEFUN_INPUT_DIR (default /input)
and writes /output/<id>.out as {"forecasts": [{"case": id, "price": x}]}.
"""

import json
import os
import statistics
import sys

# Last 6 hours of 1-minute closes.
WINDOW = 360
# How far the forecast moves from the checkpoint close toward the median.
REVERSION_WEIGHT = 0.5
# Safety cap on the reversion move (dollars); never binds in backtest.
MAX_MOVE = 1000.0

MIN_PRICE = 0.00001
MAX_PRICE = 9_999_999.99999


def price5(x):
    """Keep a price on the grid's 5 decimals and inside (0, 10_000_000)."""
    return round(min(MAX_PRICE, max(MIN_PRICE, x)) * 1e5) / 1e5


def forecast(prices):
    if not prices:
        raise ValueError("market has no prices")
    last = prices[-1]
    window = prices[-WINDOW:]
    median = statistics.median(window)
    move = REVERSION_WEIGHT * (median - last)
    move = max(-MAX_MOVE, min(MAX_MOVE, move))
    return price5(last + move)


def main():
    input_dir = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(output_dir, exist_ok=True)
    inputs = sorted(f for f in os.listdir(input_dir) if f.endswith(".in"))
    for filename in inputs:
        case_id = filename[: -len(".in")]
        with open(os.path.join(input_dir, filename), "r", encoding="utf-8") as fh:
            case = json.load(fh)
        markets = case.get("markets")
        if not isinstance(markets, list) or len(markets) != 1:
            raise ValueError(f"{filename} does not hold exactly one market")
        price = forecast(markets[0]["prices"])
        out = {"forecasts": [{"case": case_id, "price": price}]}
        with open(os.path.join(output_dir, case_id + ".out"), "w", encoding="utf-8") as fh:
            fh.write(json.dumps(out) + "\n")


if __name__ == "__main__":
    main()
