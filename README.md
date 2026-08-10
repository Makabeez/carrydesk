# CarryDesk

An autonomous carry desk. Reads Hyperliquid perpetual funding rates, compares annualised carry against the onchain savings rate, and rotates real capital between venues when the spread justifies the move.

**KeeperHub "Agents Onchain" — DoraHacks hackathon · deadline 13 Aug 2026**

---

## Live onchain evidence

All transactions on Ethereum mainnet, gas sponsored by KeeperHub:

| date | action | amount | tx |
|---|---|---|---|
| 2026-08-09 | DAI approve (path validation) | — | [0x11ad27a6...](https://etherscan.io/tx/0x11ad27a6f4aeec8ca74358800bec3340c687d8e6769cac4913adb3e7449e6897) |
| 2026-08-10 | sDAI deposit (path validation) | 0 DAI | [0xe17e6c20...](https://etherscan.io/tx/0xe17e6c2083ae00039199b2317a9fbeaa495ce4532c3002e6b1bff2af7dea66be) |
| 2026-08-10 | DAI approve (funded run) | 1.913 DAI | [0xe4e30518...](https://etherscan.io/tx/0xe4e305184a8f3608d560fe17338a316dc36f8820847a81012a3e43ef011e1464) |
| 2026-08-10 | **sDAI deposit — funded run** | **1.913 DAI** | [**0xad85906c...**](https://etherscan.io/tx/0xad85906cbcf69d6d25c3210b52eba3dc9484ccd0ead6c001ca84863c0eb699c8) |

Position live as of 2026-08-10: **1.622 sDAI** accruing yield in Spark vault at `0x972A2E27b32152064F65a3Dda489F3899A168a37`.
Full run logs and KeeperHub execution IDs: [`evidence/`](evidence/).

---

## Measured result

Getting rotation *discipline* wrong costs 10× more than getting the *signal* wrong.

![Benchmark chart: best vs worst config across BTC ETH SOL HYPE](https://raw.githubusercontent.com/Makabeez/carrydesk/main/benchmark.svg)

| config | 90d PnL on $10k |
|---|---|
| Best: EMA-72, entry spread +3%, exit 0% | +$41 over reference rate |
| Worst: EMA-6, entry spread +1%, exit 0% | −$213 vs reference rate |
| Do nothing (hold reference rate) | $117 |

The reactive configuration turns a +$117 do-nothing baseline into a loss. The thresholds are derived from `sweep.py` on 90 days of real Hyperliquid data — not asserted. → [BENCHMARKS.md](BENCHMARKS.md)

---

## Architecture

Three KeeperHub workflows form a closed loop:

```
WF-1  carrydesk-signal   (hourly schedule · x402 paid listing)
  hyperliquid/funding-history 72h
  → code: EMA-72 → spread vs reference rate
  → aave-v3/get-user-reserve-data  (reference rate, live onchain)
  → emit { state: ENTER/HOLD/EXIT, spread, ema_apr, reference_apr }
         │
         ▼ webhook
WF-2  carrydesk-rotate   (webhook trigger)
  budget-gate (1 rotation/day hard cap)
  ENTER: idempotency-check → dai-balance
       → web3/approve-token (exact amount, not max)
       → spark/vault-deposit → spark/vault-balance (read-back verify)
  EXIT:  spark/vault-balance → spark/vault-redeem
       → web3/check-token-balance (verify DAI received)
       → aave-v3/supply → aave-v3/get-user-reserve-data (read-back)

WF-3  carrydesk-guard    (every 15 min)
  spark/vault-balance + aave-v3/get-user-reserve-data
  → code: alert if position split across both venues or missing from both
  → webhook/send-webhook → WF-2 EXIT
```

---

## Reproduce the benchmark

No wallet, no RPC key, no API key needed:

```bash
git clone https://github.com/Makabeez/carrydesk
cd carrydesk
python3 funding_bench.py --coins BTC ETH SOL HYPE --days 90
python3 sweep.py --coins BTC ETH SOL HYPE --days 90
```

Pulls from Hyperliquid's public `fundingHistory` endpoint. Takes ~30s.

---

## KeeperHub surfaces used

- `hyperliquid/funding-history` — 72h bulk historical pull (not the live snapshot)
- `spark/vault-balance`, `spark/vault-deposit`, `spark/vault-redeem`
- `aave-v3/supply`, `aave-v3/get-user-reserve-data`
- `web3/check-token-balance`, `web3/approve-token`
- `webhook/send-webhook` (WF-3 → WF-2 guard trigger)
- `code/run-code` (EMA, hysteresis, rotation budget, position guard)
- x402 paid listing — WF-1 signal workflow, callable by other agents at $0.10/call

---

## Files

| path | what |
|---|---|
| `funding_bench.py` | 90-day funding analysis — all thresholds measured here |
| `sweep.py` | EMA × hysteresis grid search → derives `carrydesk.config.json` |
| `carrydesk.config.json` | Frozen rotation parameters (output of `sweep.py`) |
| `BENCHMARKS.md` | Full measured results + honest limits + REAL/SIMULATED table |
| `workflows/` | Exported WF-1/2/3 JSON (importable) |
| `evidence/` | Onchain tx evidence with KeeperHub execution IDs and Etherscan links |
| `onboarding-teardown.md` | 12 findings from first-run; 4 PRs filed upstream |

---

## Onboarding teardown

12 findings across first-run on Linux/WSL, headless. Four upstream PRs filed:

| # | repo | type |
|---|---|---|
| [KeeperHub/cli#87](https://github.com/KeeperHub/cli/pull/87) | cli | Bug: numeric `chainId` unmarshal crash |
| [KeeperHub/cli#88](https://github.com/KeeperHub/cli/pull/88) | cli | Docs: Linux install + device-code auth |
| [KeeperHub/cli#89](https://github.com/KeeperHub/cli/pull/89) | cli | Bug: npx binary name inference breaks all wallet subcommands |
| [KeeperHub/claude-plugins#5](https://github.com/KeeperHub/claude-plugins/pull/5) | claude-plugins | Docs: SSH prereq + MCP fallback |

Full notes including the undocumented executing wallet, wei/human unit mismatch, and self-webhook DNS limitation: [onboarding-teardown.md](onboarding-teardown.md)
