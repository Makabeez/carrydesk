#!/usr/bin/env python3
"""
CarryDesk sweep: find the rotation band by backtest, don't assert it.

Reuses the API layer from funding_bench.py. Every parameter shipped in the
agent config comes from this sweep's output, on real Hyperliquid data.

Usage:  python3 sweep.py --coins BTC ETH SOL HYPE --days 90
"""
import argparse, json
from itertools import product

from funding_bench import funding_history, annualized, HOURS_PER_YEAR


def ema(xs, n):
    k = 2 / (n + 1)
    cur, out = xs[0], []
    for x in xs:
        cur = x * k + cur * (1 - k)
        out.append(cur)
    return out


def backtest(apr, win, entry, exit_, ssr, notional, gas):
    """Hysteresis rotation. entry/exit are SPREAD over the reference rate.
    Capital is always deployed: either in carry, or in the reference rate."""
    sig = ema(apr, win)
    pos, pnl, rotations = 0, 0.0, 0
    for i, a in enumerate(apr):
        pnl += (a if pos else ssr) * notional / 100 / HOURS_PER_YEAR
        s = sig[i] - ssr
        if pos == 0 and s > entry:
            pos, rotations = 1, rotations + 1
            pnl -= gas / 2
        elif pos == 1 and s < exit_:
            pos, rotations = 0, rotations + 1
            pnl -= gas / 2
    hold = ssr * notional / 100 / HOURS_PER_YEAR * len(apr)
    return pnl, hold, rotations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coins", nargs="+", default=["BTC", "ETH", "SOL", "HYPE"])
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--ssr", type=float, default=4.75)
    ap.add_argument("--notional", type=float, default=10_000)
    ap.add_argument("--gas", type=float, default=6.0)
    ap.add_argument("--windows", nargs="+", type=int, default=[6, 24, 72])
    ap.add_argument("--entries", nargs="+", type=float, default=[1, 3, 6])
    ap.add_argument("--exits", nargs="+", type=float, default=[-2, 0, 1])
    a = ap.parse_args()

    chosen = {}
    print("| coin | EMA(h) | entry | exit | rotations | strategy $ | hold-ref $ | edge $ |")
    print("|---|---|---|---|---|---|---|---|")
    for coin in a.coins:
        apr = annualized(funding_history(coin, a.days))
        res = []
        for w, e, x in product(a.windows, a.entries, a.exits):
            if x >= e:
                continue
            p, h, r = backtest(apr, w, e, x, a.ssr, a.notional, a.gas)
            res.append((p - h, w, e, x, r, p, h))
        res.sort(reverse=True)
        for tag, row in (("", res[0]), (" (worst cfg)", res[-1])):
            edge, w, e, x, r, p, h = row
            print(f"| {coin}{tag} | {w} | {e:+g} | {x:+g} | {r} | "
                  f"{p:,.0f} | {h:,.0f} | {edge:+,.0f} |")
        chosen[coin] = {"ema_hours": res[0][1], "entry_spread": res[0][2],
                        "exit_spread": res[0][3]}
    print("\n// carrydesk.config.json")
    print(json.dumps(chosen, indent=2))


if __name__ == "__main__":
    main()
