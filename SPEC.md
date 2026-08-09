# CarryDesk — build spec

**Event:** KeeperHub "Agents Onchain" (DoraHacks) · deadline **13 Aug 2026, 12:00 UTC+2**
**Judging:** execution weighted heavily · KeeperHub surfaces used · reliability &
observability · originality/usefulness · integration quality
**Required at submission:** GitHub repo · demo video of the agent executing onchain
through KeeperHub · link to a transaction the agent executed

---

## 1. Pitch (first two sentences — problem, then wedge)

> Capital sitting onchain earns the savings rate while the perp market is paying
> three times that — or the reverse, twice a week. CarryDesk reads Hyperliquid
> funding, decides which side of that spread to be on, and rotates real capital
> through KeeperHub — and we measured that getting the *rotation discipline*
> wrong costs 10x more than getting the *signal* right.

Five-second non-crypto test: *"It parks your cash wherever it earns most, and
watches the futures market to know when to move it."*

---

## 2. Why this wins here

- **Uses the plugin nobody uses.** KeeperHub ships a Hyperliquid plugin whose
  `Get Funding History` action is documented for "basis-trade signal
  generation". The April OpenAgents cohort (ChainShield, CactusNetwork, Hermes,
  DeFi Swarm, AgentMesh, Keeperhub Matcha) shipped guardrails, swaps, rebalancers
  and SDK wrappers. Nobody touched funding.
- **The benchmark is the differentiator.** `fundingHistory` is a bulk historical
  endpoint — the quantitative proof is native, not bolted on.
- **The honest negative result is the story**, and it flatters the sponsor:
  reactive rotation destroys the position; execution discipline is where the
  money is. That is KeeperHub's own thesis, proven with numbers rather than
  asserted in a pitch.
- **The agent invoices.** The funding-signal workflow is published as a paid
  listing — callers pay per execution in USDC via x402, indexed on x402scan.

---

## 3. Workflow graph

Confirm node/field names against `docs.keeperhub.com/workflows/schema-reference`
before wiring — the shape below is the logic, not the literal JSON.

### WF-1 · `carrydesk-signal` (published, paid via x402)

```
Trigger: Schedule — hourly
  → Hyperliquid: Get Funding History   (coin, startTime = now-72h)
  → Code: EMA-72 over annualized rate; spread = ema - reference_rate
  → Web3: read reference rate onchain   (savings-rate contract)
  → Code: emit {coin, funding_apr, ema_apr, reference_apr, spread, state}
  → return  (this is the paid output — no writes, no wallet needed)
```

Read-only, so it is cheap to run, safe to expose, and it is the thing other
agents actually want to buy. List it; the 402 challenge and payment settle
without you in the loop.

### WF-2 · `carrydesk-rotate` (the execution half)

```
Trigger: Webhook  (fired by WF-1 or by the agent)
  → Condition: state == ENTER ?
      ├─ true  → Web3: read current allocation + wallet balance
      │          → Condition: already deployed ? → exit (idempotent, no-op)
      │          → Web3: approve (exact amount, not max)
      │          → Web3: deposit into carry venue
      │          → Web3: read back position  (verify, don't assume)
      │          → Telegram: rotation report — direction, spread, tx hash, gas
      └─ false → Condition: state == EXIT ?
                 → Web3: withdraw → redeploy to reference rate
                 → Web3: read back → Telegram report
  On any step failure: retry per KeeperHub policy, then Telegram: PAGE + halt
```

**Non-negotiables in this graph** (these are the reliability score):
- Every write is preceded by a read and followed by a read-back verification.
- Idempotency guard: re-firing the webhook must not double-deposit.
- Exact-amount approvals, never `max`.
- A rotation-budget counter: hard cap on rotations per 24h. The sweep says the
  correct number is ~1 per 2 weeks; anything more is the failure mode we
  measured.
- Halt-on-repeat-failure rather than infinite retry.

### WF-3 · `carrydesk-guard` (cheap, high-signal)

```
Trigger: Block interval
  → Web3: read deployed position value + reference position
  → Condition: drift > tolerance OR position missing ?
      → Telegram: PAGE + fire WF-2 EXIT
```

Answers "does the build understand failure modes?" with a workflow rather than
a paragraph.

---

## 4. Repos

**`carrydesk`** — the desk
```
agent/            MCP client; calls KeeperHub tools; decides ENTER/HOLD/EXIT
workflows/        exported WF-1..WF-3 JSON (importable by a judge)
bench/            funding_bench.py, sweep.py
web/              hero UI: live spread vs reference, regime band,
                  rotation timeline with tx links, run log
BENCHMARKS.md     measured results + honest limits + REAL/SIMULATED table
README.md         pitch, one-command demo, tx links
```

**`carrydesk-kit`** — fork-and-run primitives
```
funding-signal/   the EMA + hysteresis primitive, venue-agnostic
workflow-templates/  WF-1..WF-3 as parameterised templates
scripts/demo.sh   full cycle in < 90s, no wallet, no RPC key, read-only path
README.md         "exposes: funding regime detection, hysteresis rotation band,
                   read-back-verified execution, rotation budget guard"
```

Judge path must be: click live URL → see the desk → one command → see a cycle.

---

## 5. Plan

**Today (5 Aug, 30 min)** — register the BUIDL on DoraHacks; join the builder
channel; ask (a) Grand Prize amounts, (b) whether pre-existing code is allowed
or only the KeeperHub integration must be fresh. Create the org at
app.keeperhub.com (Turnkey wallet auto-provisioned), grab the `kh_` API key,
fund on Sepolia, land one trivial tx tonight. *Platform de-risked before crunch.*

**6–8 Aug** — Clearloop only. Nothing here.

**9 Aug** — Clearloop MVP ships.

**10 Aug** — WF-1 + WF-2 wired and firing on Sepolia. Sweep re-run, config
frozen from its output. First real rotation executed.

**11 Aug** — Mainnet rotation (gas is sponsored on mainnet — use it, it is the
differentiator and it is free). WF-3 guard. Publish WF-1 as a paid x402 listing.
Hero UI. Recruit 3–5 callers for the paid workflow from the builder channel —
*not self-paid.*

**12 Aug — stop coding.** Video (60–90s, hook in 5s, one real onchain action
with explorer visible, CTA). README + BENCHMARKS final. Onboarding-bounty
teardown written from the Day-0 notes. Submit — do not wait for the 13th.

**13 Aug** — verify on the DoraHacks page that the BUIDL is registered and
complete. Then stop.

---

## 6. Submission checklist (blocking — no item is optional)

- [ ] Live URL a judge can click, no login
- [ ] One-command reproduction path, no wallet/RPC/token, < 60s
- [ ] Every threshold measured by `sweep.py`, none asserted
- [ ] Honest limit + negative result published (§4 of BENCHMARKS.md)
- [ ] REAL / SIMULATED table written before a judge asks
- [ ] Historical/bulk endpoint used, not just the live snapshot ✔ `fundingHistory`
- [ ] At least one linked explorer tx per onchain claim
- [ ] Sold to a buyer (paid x402 listing), not to an observer
- [ ] Demo video ≤ 90s with a real onchain action visible
- [ ] BUIDL confirmed registered on the DoraHacks page while the window is open
- [ ] Onboarding-bounty submission filed separately ($1,000 split two ways,
      stackable with the Grand Prize)
- [ ] Announcement thread from @GeiserJoe2, tagging KeeperHub

---

## 7. Risks

| risk | mitigation |
|---|---|
| Carry venue integration deeper than expected | Fall back to the simplest two-venue pair; the thesis is the rotation, not the venue |
| Mainnet gas sponsorship has caveats | Ask in the builder channel today, not on the 11th |
| Edge is thin ($41–123/90d on $10k) | Do not pitch profit. Pitch *execution discipline vs. reactivity* — that is the measured result and it is worth more |
| Clearloop overruns into the 10th | Kill Walrus now, not on the 9th |
