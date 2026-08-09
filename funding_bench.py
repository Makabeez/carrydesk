#!/usr/bin/env python3
"""
CarryDesk benchmark: derive rotation thresholds from REAL Hyperliquid funding history.

No asserted constants. Every threshold in the README comes out of this script.

Usage:  python3 funding_bench.py --coins BTC ETH SOL --days 90 --ssr 4.75
"""
import argparse, json, statistics as st, time, urllib.request

INFO = "https://api.hyperliquid.xyz/info"
HOURS_PER_YEAR = 24 * 365


def post(payload, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(
                INFO, data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            if i == retries - 1:
                raise
            time.sleep(1.5 * (i + 1))


def funding_history(coin, days):
    """API caps at 500 rows/call (~21d hourly). Paginate forward."""
    end = int(time.time() * 1000)
    start = end - days * 24 * 3600 * 1000
    out, cursor, seen = [], start, set()
    while cursor < end:
        batch = post({"type": "fundingHistory", "coin": coin,
                      "startTime": cursor, "endTime": end})
        if not batch:
            break
        fresh = [r for r in batch if r["time"] not in seen]
        for r in fresh:
            seen.add(r["time"])
        out.extend(fresh)
        last = batch[-1]["time"]
        if last <= cursor:
            break
        cursor = last + 1
    out.sort(key=lambda r: r["time"])
    return out


def annualized(rows):
    return [float(r["fundingRate"]) * HOURS_PER_YEAR * 100 for r in rows]


def pct(xs, p):
    xs = sorted(xs)
    k = (len(xs) - 1) * p / 100
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def run_lengths(apr, threshold):
    """How many consecutive hours funding stays above `threshold` (%APR).
    This is the persistence question: a spread you cannot hold long enough
    to amortize gas is not an opportunity."""
    runs, cur = [], 0
    for a in apr:
        if a > threshold:
            cur += 1
        elif cur:
            runs.append(cur); cur = 0
    if cur:
        runs.append(cur)
    return runs


def breakeven_hours(spread_apr, notional, gas_usd_roundtrip):
    """Hours of carry needed to repay one in+out rotation."""
    if spread_apr <= 0:
        return float("inf")
    hourly = notional * (spread_apr / 100) / HOURS_PER_YEAR
    return gas_usd_roundtrip / hourly if hourly > 0 else float("inf")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coins", nargs="+", default=["BTC", "ETH", "SOL"])
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--ssr", type=float, default=4.75,
                    help="onchain reference rate %%APR (Sky Savings Rate / sDAI)")
    ap.add_argument("--notional", type=float, default=10_000)
    ap.add_argument("--gas", type=float, default=6.0,
                    help="USD cost of one in+out rotation")
    a = ap.parse_args()

    print(f"# CarryDesk measured benchmark")
    print(f"source: Hyperliquid Info API `fundingHistory` | window: {a.days}d | "
          f"reference rate: {a.ssr}%% APR | notional ${a.notional:,.0f} | "
          f"rotation cost ${a.gas}\n")

    for coin in a.coins:
        rows = funding_history(coin, a.days)
        if not rows:
            print(f"## {coin}: no data\n"); continue
        apr = annualized(rows)
        spread = [x - a.ssr for x in apr]
        neg = sum(1 for x in apr if x <= 0) / len(apr) * 100
        below = sum(1 for x in spread if x <= 0) / len(spread) * 100

        print(f"## {coin}  (n={len(apr)} hourly observations)")
        print(f"  funding %APR   mean {st.mean(apr):6.2f} | median {st.median(apr):6.2f} "
              f"| p10 {pct(apr,10):6.2f} | p90 {pct(apr,90):6.2f} | max {max(apr):6.2f}")
        print(f"  hours funding <= 0 .............. {neg:5.1f}%")
        print(f"  hours funding <= reference rate .. {below:5.1f}%   <-- rotation would LOSE")

        for thr in (0, a.ssr, a.ssr + 5, a.ssr + 10):
            runs = run_lengths(apr, thr)
            med = st.median(runs) if runs else 0
            p90 = pct(runs, 90) if runs else 0
            share = sum(runs) / len(apr) * 100 if runs else 0
            print(f"  above {thr:5.2f}%APR: {share:5.1f}% of hours | "
                  f"{len(runs):3d} regimes | median run {med:5.1f}h | p90 run {p90:6.1f}h")

        med_spread = st.median(spread)
        be = breakeven_hours(med_spread, a.notional, a.gas)
        print(f"  breakeven at median spread ({med_spread:.2f}%APR): "
              f"{be:.1f}h of holding to repay ${a.gas} rotation")
        for s in (5, 10, 20):
            print(f"    at {s}%APR spread: {breakeven_hours(s, a.notional, a.gas):.1f}h")
        print()


if __name__ == "__main__":
    main()
