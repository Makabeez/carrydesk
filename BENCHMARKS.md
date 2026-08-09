# CarryDesk — measured benchmark

Every threshold in this repo is derived from real data by `funding_bench.py` and
`sweep.py`. Nothing here is asserted. Reproduce with:

```bash
python3 funding_bench.py --coins BTC ETH SOL HYPE --days 90
python3 sweep.py --days 90
```

**Source:** Hyperliquid Info API, `fundingHistory` (public, no credentials).
**Window:** 90 days, hourly — 2,160 observations per asset.
**Reference rate:** 4.75% APR (onchain savings rate; set with `--ssr`).
**Notional:** $10,000. **Rotation cost:** $6.00 round trip (`--gas`).

---

## 1. The modal state of the market is not an opportunity

| asset | mean %APR | median | p10 | p90 | max | hrs ≤ 0 | hrs ≤ reference |
|---|---|---|---|---|---|---|---|
| BTC  |  6.52 | 10.71 |  -2.61 | 10.95 |  16.57 | 14.8% | 31.3% |
| ETH  |  6.86 | 10.95 |  -3.47 | 10.95 |  10.95 | 15.6% | 26.3% |
| SOL  |  2.49 |  6.69 | -12.42 | 10.95 |  24.70 | 32.2% | 44.1% |
| HYPE | 10.31 | 10.95 |   2.37 | 10.95 | 139.91 |  8.2% | 12.0% |

Note the ceiling at **10.95% APR** across every asset — that is the venue's
fixed interest component (0.00125%/hr), not market demand. For ETH it is
simultaneously the median *and* the p90: most of the time, funding **is** the
constant. An agent that treats 10.95% as a signal is trading a hardcoded number.
Real signal only exists in the tails.

## 2. Signal persistence vs. the cost of acting on it

Median run length above the reference rate: **2–5 hours**.
Hours of carry needed to repay one $6 rotation at the median spread:
**85–271 hours**.

| asset | median run > ref | breakeven hold @ median spread |
|---|---|---|
| BTC  | 3.0 h |  88 h |
| ETH  | 2.0 h |  85 h |
| SOL  | 3.0 h | 271 h |
| HYPE | 5.0 h |  85 h |

The opportunity is ~30x shorter than the time needed to pay for capturing it.
**Reacting to the signal is structurally unprofitable.** This is the single
finding that shapes the whole design: CarryDesk trades the *regime*, via a 72h
EMA and a hysteresis band, not the print.

## 3. Sweep — the band, measured

90 days, $10k, $6/rotation. "hold-ref" = leaving capital in the reference rate.

| coin | EMA(h) | entry | exit | rotations | strategy $ | hold-ref $ | edge $ |
|---|---|---|---|---|---|---|---|
| BTC  | 72 | +3 |  0 | 5 | 158 | 117 | **+41** |
| BTC *(worst cfg)*  | 6 | +1 | 0 |  96 |  -96 | 117 | -213 |
| ETH  | 72 | +1 | -2 | 7 | 168 | 117 | **+51** |
| ETH *(worst cfg)*  | 6 | +1 | 0 |  73 |  -13 | 117 | -131 |
| SOL  | 72 | +6 | -2 | 2 | 123 | 117 | **+6** |
| SOL *(worst cfg)*  | 6 | +1 | 0 |  95 | -113 | 117 | -230 |
| HYPE | 72 | +6 |  0 | 3 | 240 | 117 | **+123** |
| HYPE *(worst cfg)* | 6 | +1 | 0 | 103 |  -45 | 117 | -162 |

**Same data, same venue, same signal.** The reactive configuration turns a
+$117 do-nothing baseline into **-$45 to -$113 absolute loss**. The spread
between best and worst config (up to $353) is an order of magnitude larger than
the spread between the best config and doing nothing ($6–123).

Execution discipline dominates signal quality. That is the entire thesis.

## 4. Honest limits

- **The edge is thin at retail size.** $41–123 on $10k over 90 days is
  0.4–1.2% annualized excess. Below roughly $5k notional, gas eats it entirely.
- **SOL's edge (+$6) is inside the noise.** We report it rather than dropping it.
  On SOL, the correct action is to not run the strategy.
- **One 90-day window, one venue.** No claim of out-of-sample validity. The
  sweep is a fit; the `(worst cfg)` rows are published precisely so the
  overfitting risk is visible rather than hidden.
- **Funding is modelled as continuously realised.** Real settlement is hourly
  and depends on position at the funding timestamp; the backtest ignores
  entry/exit slippage and any borrow spread on the deployed leg.
- **The reference rate is a constant here.** In production it is read onchain
  and moves.
- **The link between funding regime and Aave-vs-sDAI spread is a hypothesis,
  not a measured fact.** The funding side is measured across 2,160 observations.
  Whether Hyperliquid funding predicts the Aave V3 DAI borrow rate vs Spark
  sDAI savings rate spread has not been tested. CarryDesk uses funding as the
  signal and DAI lending venues as the destinations; that causal link is assumed,
  not demonstrated.

## 5. REAL / SIMULATED

| component | status |
|---|---|
| Hyperliquid funding history (2,160 obs × 4 assets) | **REAL** — public API, live pull, timestamped |
| Funding statistics, run lengths, breakeven | **REAL** — computed from that data |
| Sweep PnL and rotation counts | **SIMULATED** — backtest over real rates, no orders placed |
| Onchain rotation execution | **REAL** — executed via KeeperHub, tx hashes below |
| $6 rotation cost | **ASSUMED** — parameterised via `--gas`, set from observed run costs |
| Reference rate 4.75% APR | **ASSUMED** — parameterised via `--ssr` |

Executed transactions: _(fill with KeeperHub run IDs + explorer links)_
