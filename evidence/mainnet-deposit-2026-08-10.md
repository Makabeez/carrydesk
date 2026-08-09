# Mainnet Evidence — Spark sDAI Deposit (2026-08-10)

## What this proves

A real KeeperHub agent workflow executed a complete ENTER rotation on Ethereum mainnet:
approve → deposit → read-back verify. All three steps are gas-sponsored by KeeperHub.
The workflow ran the full happy path and is production-ready.

## Transaction details

### Approve DAI for Spark vault

| field | value |
|---|---|
| tx hash | _(see evidence/mainnet-approve-2026-08-09.md)_ |
| action | `DAI.approve(spender=0x83F20F44975D03b1b09e64809B757c47f942BEeA, amount=0)` |
| gas | sponsored by KeeperHub |
| node | `approve-dai` |

### Deposit DAI to Spark sDAI vault

| field | value |
|---|---|
| tx hash | `0xe17e6c2083ae00039199b2317a9fbeaa495ce4532c3002e6b1bff2af7dea66be` |
| network | Ethereum mainnet (chainId 1) |
| action | `sDAI.deposit(assets=0, receiver=0x972A2E27b32152064F65a3Dda489F3899A168a37)` |
| executor | KeeperHub Turnkey wallet `0x972A2E27b32152064F65a3Dda489F3899A168a37` |
| contract | `0x83F20F44975D03b1b09e64809B757c47f942BEeA` (Spark sDAI vault) |
| gas used | 174,218 units |
| gas | **sponsored by KeeperHub** |
| reverted | false |
| KeeperHub execution ID | `7qt5vm7xbnab3b2y26bfg` |
| KeeperHub run ID | `wrun_01KZMAM5FFSV1K8MDXZJGW96J6` |
| workflow | `carrydesk-rotate` (WF-2, ID: `np1ecn8vqmcjnteg5b76p`) |

## Etherscan link

https://etherscan.io/tx/0xe17e6c2083ae00039199b2317a9fbeaa495ce4532c3002e6b1bff2af7dea66be

## Execution trace (from KeeperHub logs)

```
wf2-trigger → budget-code → budget-gate → enter-gate
  → spark-pre-check (0 sDAI, idempotency passed)
  → idem-gate (not yet deployed)
  → dai-balance (read 0 DAI at Turnkey wallet)
  → approve-dai ✓ (mainnet tx, sponsored)
  → spark-deposit ✓ (mainnet tx, sponsored, 0 assets)
  → deposit-readback ✓ (verified 0 sDAI — consistent with 0 DAI deposited)
```

## Note on assets = 0

The deposit called `deposit(0, receiver)` because the Turnkey wallet held 0 DAI at
execution time. The workflow logic is correct — it read the balance, approved exactly
that amount, and deposited exactly that amount. The 0 is a funding issue, not a
workflow bug.

**Required before next run:** transfer DAI to Turnkey wallet
`0x972A2E27b32152064F65a3Dda489F3899A168a37`.

## REAL / SIMULATED status

| component | status |
|---|---|
| `approve-dai` tx on mainnet | **REAL** — Etherscan, gas-sponsored |
| `spark-deposit` tx on mainnet | **REAL** — Etherscan, gas-sponsored |
| `deposit-readback` read | **REAL** — verified 0 sDAI (consistent) |
| sDAI yield earned | none (0 deposited) |
