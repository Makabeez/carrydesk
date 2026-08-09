# Mainnet Evidence — DAI Approve (2026-08-09)

## What this proves

A real KeeperHub agent workflow executed an ERC-20 approval on Ethereum mainnet.
This is not a simulated action — the transaction is indexed on Etherscan.

## Transaction details

| field | value |
|---|---|
| tx hash | `0x11ad27a6f4aeec8ca74358800bec3340c687d8e6769cac4913adb3e7449e6897` |
| network | Ethereum mainnet |
| action | `DAI.approve(spender=Spark, amount=...)` |
| executor | KeeperHub Turnkey wallet `0x972A2E27b32152064F65a3Dda489F3899A168a37` |
| KeeperHub execution ID | `c4njod6fjhbupzk63hgtm` |
| KeeperHub run ID | `wrun_01KZM9VADZRFJ6H95XZ5NT9CB3` |
| workflow | `carrydesk-rotate` (WF-2, ID: `np1ecn8vqmcjnteg5b76p`) |
| node | `approve-dai` |
| gas | sponsored by KeeperHub (`sponsored: true`) |

## Etherscan link

https://etherscan.io/tx/0x11ad27a6f4aeec8ca74358800bec3340c687d8e6769cac4913adb3e7449e6897

## Context

This approve was triggered by a WF-2 ENTER run. The workflow correctly:
1. Read DAI balance from the wallet
2. Approved the exact DAI amount (not `max`) to the Spark vault spender
3. Attempted deposit — which failed at that step due to DAI being in the wrong wallet
   (KeeperHub executes from Turnkey wallet `0x972A2E…`, not the source wallet `0xe1dC…`)

The approve tx itself is valid proof of agent execution through KeeperHub on mainnet.

## Fix applied after this run

- DAI transferred from `0xe1dC20C4Ed70b281441FA9b8324168DF4bdC11be` → `0x972A2E27b32152064F65a3Dda489F3899A168a37`
- WF-2 `dai-balance` node address updated to `0x972A2E27b32152064F65a3Dda489F3899A168a37`
