#!/usr/bin/env python3
"""
CarryDesk: render the headline benchmark as an SVG.

The point of the chart is one comparison: the same signal, on the same data,
with a reactive band versus a patient one. No dependencies, no matplotlib.

Usage:  python3 plot_bench.py > benchmark.svg
        python3 plot_bench.py --coins BTC ETH SOL HYPE --days 90 > benchmark.svg

With no --live flag it renders the frozen numbers from BENCHMARKS.md so the
chart is reproducible; pass --live to re-run the sweep and plot fresh values.
"""
import argparse, sys

# Frozen from BENCHMARKS.md (90d, $10k notional, $6/rotation).
FROZEN = {
    #  coin:   (best_edge, worst_edge, best_rotations, worst_rotations)
    "BTC":  (41,  -213,  5,  96),
    "ETH":  (51,  -131,  7,  73),
    "SOL":  (6,   -230,  2,  95),
    "HYPE": (123, -162,  3, 103),
}
BASELINE = 117  # do-nothing: hold the reference rate

W, H = 760, 420
PAD_L, PAD_R, PAD_T, PAD_B = 70, 24, 64, 76

FG = "#111827"
MUTED = "#6B7280"
GOOD = "#047857"
BAD = "#B91C1C"
BASE = "#9CA3AF"
GRID = "#E5E7EB"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(data, baseline):
    coins = list(data)
    lo = min(min(v[1] for v in data.values()), 0, baseline) - 40
    hi = max(max(v[0] for v in data.values()), baseline) + 40

    plot_w = W - PAD_L - PAD_R
    plot_h = H - PAD_T - PAD_B

    def y(val):
        return PAD_T + plot_h * (hi - val) / (hi - lo)

    band = plot_w / len(coins)
    bw = band * 0.26

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif">',
        f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
        f'<text x="{PAD_L}" y="30" font-size="17" font-weight="600" fill="{FG}">'
        f'Same data, same signal — the band decides the outcome</text>',
        f'<text x="{PAD_L}" y="50" font-size="12.5" fill="{MUTED}">'
        f'90 days of Hyperliquid funding, $10,000 notional, $6 per rotation. '
        f'Dashed line = doing nothing.</text>',
    ]

    # gridlines
    step = 100
    v = int(lo // step) * step
    while v <= hi:
        yy = y(v)
        out.append(f'<line x1="{PAD_L}" y1="{yy:.1f}" x2="{W-PAD_R}" y2="{yy:.1f}" '
                   f'stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{PAD_L-10}" y="{yy+4:.1f}" font-size="11" fill="{MUTED}" '
                   f'text-anchor="end">${v:,}</text>')
        v += step

    # zero line
    out.append(f'<line x1="{PAD_L}" y1="{y(0):.1f}" x2="{W-PAD_R}" y2="{y(0):.1f}" '
               f'stroke="{MUTED}" stroke-width="1.25"/>')

    # baseline
    yb = y(baseline)
    out.append(f'<line x1="{PAD_L}" y1="{yb:.1f}" x2="{W-PAD_R}" y2="{yb:.1f}" '
               f'stroke="{BASE}" stroke-width="1.5" stroke-dasharray="6 4"/>')
    out.append(f'<text x="{W-PAD_R}" y="{yb-7:.1f}" font-size="11" fill="{MUTED}" '
               f'text-anchor="end">do nothing  ${baseline}</text>')

    for i, coin in enumerate(coins):
        best, worst, rb, rw = data[coin]
        cx = PAD_L + band * (i + 0.5)

        for val, off, colour, rot in ((best, -bw*0.62, GOOD, rb),
                                      (worst, bw*0.62, BAD, rw)):
            x0 = cx + off - bw / 2
            top = y(max(val, 0))
            height = abs(y(val) - y(0))
            out.append(f'<rect x="{x0:.1f}" y="{top:.1f}" width="{bw:.1f}" '
                       f'height="{height:.1f}" fill="{colour}" rx="2"/>')
            ly = top - 7 if val >= 0 else top + height + 15
            out.append(f'<text x="{cx+off:.1f}" y="{ly:.1f}" font-size="11.5" '
                       f'font-weight="600" fill="{colour}" text-anchor="middle">'
                       f'{"+" if val >= 0 else "−"}${abs(val)}</text>')
            out.append(f'<text x="{cx+off:.1f}" y="{ly + (-14 if val >= 0 else 13):.1f}" '
                       f'font-size="10" fill="{MUTED}" text-anchor="middle">'
                       f'{rot} rotations</text>')

        out.append(f'<text x="{cx:.1f}" y="{H-PAD_B+26:.1f}" font-size="13" '
                   f'font-weight="600" fill="{FG}" text-anchor="middle">{esc(coin)}</text>')

    ly = H - 22
    out.append(f'<rect x="{PAD_L}" y="{ly-9}" width="11" height="11" fill="{GOOD}" rx="2"/>')
    out.append(f'<text x="{PAD_L+18}" y="{ly}" font-size="11.5" fill="{FG}">'
               f'EMA-72, wide hysteresis band</text>')
    out.append(f'<rect x="{PAD_L+232}" y="{ly-9}" width="11" height="11" fill="{BAD}" rx="2"/>')
    out.append(f'<text x="{PAD_L+250}" y="{ly}" font-size="11.5" fill="{FG}">'
               f'EMA-6, tight band (reactive)</text>')

    out.append('</svg>')
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true",
                    help="re-run the sweep instead of using frozen numbers")
    ap.add_argument("--coins", nargs="+", default=list(FROZEN))
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--ssr", type=float, default=4.75)
    ap.add_argument("--notional", type=float, default=10_000)
    ap.add_argument("--gas", type=float, default=6.0)
    a = ap.parse_args()

    if not a.live:
        data = {c: FROZEN[c] for c in a.coins if c in FROZEN}
        baseline = BASELINE
    else:
        from itertools import product
        from funding_bench import funding_history, annualized, HOURS_PER_YEAR
        from sweep import backtest
        data, baseline = {}, None
        for coin in a.coins:
            apr = annualized(funding_history(coin, a.days))
            res = []
            for w, e, x in product([6, 24, 72], [1, 3, 6], [-2, 0, 1]):
                if x >= e:
                    continue
                p, h, r = backtest(apr, w, e, x, a.ssr, a.notional, a.gas)
                res.append((p - h, r, h))
            res.sort(reverse=True)
            data[coin] = (round(res[0][0]), round(res[-1][0]), res[0][1], res[-1][1])
            baseline = round(res[0][2])
        print(f"rendered from live sweep ({a.days}d)", file=sys.stderr)

    print(build(data, baseline))


if __name__ == "__main__":
    main()
