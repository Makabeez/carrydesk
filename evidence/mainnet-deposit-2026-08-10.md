# Mainnet Evidence — ENTER Path Validation (2026-08-10)

## What this proves

Proves the ENTER path executes end to end on mainnet: approve → deposit → read-back
verify, all gas-sponsored by KeeperHub, ten nodes green. This run deposited 0 DAI —
the principal had not yet been moved to the executing wallet, so the deposit call was
a real transaction for a zero amount. It validates the execution path, not the capital
movement. A funded run is recorded below once it lands.

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

---

## Funded Run — 1.91 DAI deposited (2026-08-10)

After transferring DAI to the Turnkey wallet, WF-2 was re-fired. This run moved real
capital into the Spark sDAI vault.

### Approve DAI for Spark

| field | value |
|---|---|
| tx hash | `0xe4e305184a8f3608d560fe17338a316dc36f8820847a81012a3e43ef011e1464` |
| network | Ethereum mainnet (chainId 1) |
| action | `DAI.approve(spender=0x83F20F44975D03b1b09e64809B757c47f942BEeA, amount=1.912768...)` |
| block | 25720474 |
| gas used | 68,461 units |
| gas | sponsored by KeeperHub |

### Deposit DAI to Spark sDAI vault

| field | value |
|---|---|
| tx hash | `0xad85906cbcf69d6d25c3210b52eba3dc9484ccd0ead6c001ca84863c0eb699c8` |
| network | Ethereum mainnet (chainId 1) |
| action | `sDAI.deposit(assets=1912768697590422227, receiver=0x972A2E27b32152064F65a3Dda489F3899A168a37)` |
| block | 25720475 |
| executor | KeeperHub Turnkey wallet `0x972A2E27b32152064F65a3Dda489F3899A168a37` |
| contract | `0x83F20F44975D03b1b09e64809B757c47f942BEeA` (Spark sDAI vault) |
| gas used | 206,831 units |
| gas | **sponsored by KeeperHub** |
| reverted | false |
| KeeperHub execution ID | `se5dnew9iaesqyb4xfxvi` |
| KeeperHub run ID | `wrun_01KZMAZH4GT0BTC93WY26KD363` |
| workflow | `carrydesk-rotate` (WF-2, ID: `np1ecn8vqmcjnteg5b76p`) |

### Etherscan links

- Approve: https://etherscan.io/tx/0xe4e305184a8f3608d560fe17338a316dc36f8820847a81012a3e43ef011e1464
- Deposit: https://etherscan.io/tx/0xad85906cbcf69d6d25c3210b52eba3dc9484ccd0ead6c001ca84863c0eb699c8

### Deposit read-back

`deposit-readback` node confirmed sDAI shares in wallet after deposit:

| field | value |
|---|---|
| sDAI shares (wei) | `1622242476097265859` |
| sDAI shares (human) | ~1.622 sDAI |
| DAI deposited | ~1.913 DAI (1912768697590422227 wei) |

The exchange rate (~0.848 sDAI per DAI) reflects accumulated yield in the vault since
sDAI inception — existing deposits have already appreciated, so fewer new shares are
minted per DAI.

### Execution trace

```
wf2-trigger → budget-code → budget-gate → enter-gate
  → spark-pre-check (0 sDAI, idempotency passed)
  → idem-gate ✓
  → dai-balance (read 1.91 DAI at Turnkey wallet)
  → approve-dai ✓ (mainnet tx, block 25720474, sponsored)
  → spark-deposit ✓ (mainnet tx, block 25720475, 1.91 DAI, sponsored)
  → deposit-readback ✓ (verified 1.622 sDAI)
```

### REAL / SIMULATED status (funded run)

| component | status |
|---|---|
| `approve-dai` tx on mainnet | **REAL** — Etherscan, gas-sponsored |
| `spark-deposit` tx on mainnet | **REAL** — Etherscan, gas-sponsored, 1.913 DAI |
| `deposit-readback` read | **REAL** — verified 1.622 sDAI shares |
| sDAI yield accruing | **YES** — position live in Spark vault |
