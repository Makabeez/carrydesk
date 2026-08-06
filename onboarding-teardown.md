# KeeperHub onboarding teardown — first run, Linux/WSL, 5 Aug 2026
Environment: Ubuntu on WSL2, x86_64, Node v24.13.0, no Homebrew, no sudo, headless (no browser on host)

1. Install docs are brew-first; no Linux path without reading GitHub Releases manually. **Doc fix: https://github.com/KeeperHub/cli/pull/88**
2. `kh --version` → "unknown flag". Correct form is `kh version`.
3. `kh auth login` documented as "opens a browser window"; actually a device-code flow. Codes expired repeatedly before I could use them on a remote/headless box. **Doc fix: https://github.com/KeeperHub/cli/pull/88**
4. `kh wallet info` shells out to `npx @keeperhub/wallet` — undocumented Node dependency, fails with "could not determine executable to run". **Doc fix: https://github.com/KeeperHub/cli/pull/88**
5. BUG: `kh w balance` → "json: cannot unmarshal number into Go struct field ChainBalance.balances.chainId of type string". API returns chainId as number, CLI v0.13.1 expects string. Reproducible on every invocation, with and without --json/--chain. **Fix: https://github.com/KeeperHub/cli/pull/87**
6. `/plugin marketplace add KeeperHub/claude-plugins` clones over SSH → "Permission denied (publickey)" without GitHub SSH keys. Blocks the documented Claude Code path entirely; the `/keeperhub:login` and `/keeperhub:status` slash commands never become available. **Doc fix: https://github.com/KeeperHub/claude-plugins/pull/5**
7. BUG (silent failure): `create_workflow` over MCP silently drops node configs when they are passed at the top level — the workflow saves without error, `execute_workflow` returns `{ status: "running" }` without error, but only the trigger node fires; all action nodes are skipped. Root cause: node config must be nested inside the `data` object (`node.data.config`, `node.data.actionType`), not at the node's top level. Nothing in the API response, the execution status, or the run log indicates the config was ignored. This is a silent-success failure: every observable signal says it worked until you check `executionTrace` and see only `["trigger-1"]`.
8. `kh run logs <id>` returns 404 for direct executions (transfers, contract calls created via `kh execute` or `execute_transfer` MCP). There is no `kh execute logs` subcommand — `kh execute --help` lists only `status`, `transfer`, and `contract-call`. The workaround is `get_direct_execution_status` over MCP, but there is no documented CLI path to retrieve logs or receipts for a non-workflow execution.

## PRs filed
| # | Repo | Type | Status |
|---|------|------|--------|
| [#87](https://github.com/KeeperHub/cli/pull/87) | KeeperHub/cli | Bug fix — accept numeric `chainId` in balance/token responses | Open |
| [#88](https://github.com/KeeperHub/cli/pull/88) | KeeperHub/cli | Docs — Linux install, device-code auth, npx prerequisite | Open |
| [#5](https://github.com/KeeperHub/claude-plugins/pull/5) | KeeperHub/claude-plugins | Docs — SSH prerequisite + MCP fallback for plugin marketplace | Open |

## Suggested fixes (remaining)
- `kh --version` should either work or print a helpful error (currently "unknown flag")
- device-code TTL should be longer or auto-refresh on headless environments
- `kh wallet info` npx dependency should ideally be vendored into the Go binary to avoid the Node requirement entirely
