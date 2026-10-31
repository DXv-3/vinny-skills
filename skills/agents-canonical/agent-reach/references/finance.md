# Finance — Xueqiu (雪球)

## Check status first

```bash
agent-reach doctor --json
```

`xueqiu.active_backend` populated = use that backend. `null` = Doctor skipped live probe (not "no backend"). Xueqiu needs a logged-in session or minimal cookie — HTTP 400 ≠ stock doesn't exist.

## OpenCLI (desktop with existing Chrome login)

```bash
opencli xueqiu whoami -f yaml            # verify login
opencli xueqiu search "英伟达" -f yaml
opencli xueqiu stock NVDA -f yaml
opencli xueqiu hot -f yaml
opencli xueqiu hot-stock -f yaml
opencli xueqiu --help                    # list all read-only commands
```

### Cookie import (if no existing session)

```bash
agent-reach configure --from-browser chrome --platform xueqiu
```

> Only reads/saves `xq_a_token` — does not touch other platform cookies.

## Acceptance / failure

- **Success**: returns stock name, code, price, or non-empty content list.
- **HTTP 400**: session/cookie issue — not "stock doesn't exist."
- `whoami` succeeds but `stock`/`hot` fails → adapter parsing / platform API issue, not auth failure.
