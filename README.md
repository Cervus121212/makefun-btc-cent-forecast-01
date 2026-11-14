# btc-cent-forecast-01 — 4-hour-ahead BTC price forecast

Forecasts Bitcoin's (cbBTC/USDC) price 240 minutes after each checkpoint,
from the 4,320 one-minute closes of the 72 hours up to the checkpoint.

## Model

Short-horizon mean reversion toward the 6-hour median:

```
forecast = last_close + 0.5 * (median(last 360 closes) - last_close)
```

with the reversion move capped at ±$1,000 (a safety bound that never binds
on any backtest case). No trend extrapolation, no fixed drift: the forecast
makes no directional bet on the final window's regime.

## Why this model

Calibrated by local backtest on the practice recording (2026-11-07..11),
three samples:

| sample | persistence MAE | this model MAE | improvement |
|---|---|---|---|
| real practice cases p00–p04 (targets = next case's checkpoint close) | 47,054.66¢ | 44,797.07¢ | −4.8% |
| 72 four-hour-spaced pseudo-cases inside the practice series | 44,356.83¢ | 42,887.86¢ | −3.3% |
| 138 two-hour-spaced pseudo-cases inside the practice series | 52,406.73¢ | 48,161.71¢ | −8.1% |

Findings that shaped the choice:

- **Trend extrapolation hurts badly.** A damped 60-minute linear-regression
  slope (×240 min, damp 0.3) scored ~30% worse than persistence; EMA
  momentum ~34% worse. At a 4-hour horizon BTC reverts, it does not trend.
- **Mean reversion helps, but the window matters.** Reversion toward the
  24-hour mean beat persistence on the pseudo-cases (+8%) yet lost on the 5
  real practice cases — regime-dependent. The 6-hour median wins on all
  three samples at every weight from 0.05 to 0.60.
- **Weight 0.5 is on the plateau.** The calibration curve is flat at
  0.5–0.6 and degrades past 0.7 on every sample, so 0.5 is a robust middle
  rather than an argmax.
- **No fixed drift.** A −$100 drift looked good on the 5 real cases
  (+12.8%) but that window was a steady downtrend; a fixed drift is a
  directional bet on an unseen regime, so it was left out.

## Running it

```sh
MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Python 3 stdlib only, deterministic (two runs produce byte-identical
outputs), ~0.01 s per case — far under the 8-second cap.

## License

MIT (see LICENSE).
