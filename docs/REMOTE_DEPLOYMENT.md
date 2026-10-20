# REB remote MCP (v0.3.0) — operator deployment guide

**Status:** protocol implementation with automated localhost OAuth/MCP tests. NOT independently certified, audited, or validated with ChatGPT's plugin review. Real DNS, TLS and account provisioning are required.

## Deployment

1. Configure `REB_DOMAIN` and `REB_PUBLIC_URL` in `.env` (see `.env.example`). Point DNS to your server. Open TCP 80 and 443. Review Caddy/TLS configuration, firewall, backups and privacy requirements.
2. Run `docker compose up -d --build`. The REB container is not directly exposed; only the HTTPS reverse proxy receives inbound connections.
3. Provision an account interactively, **without putting passwords in environment variables or shell history**: `docker compose exec reb reb-remote user-add YOUR_USERNAME`.
4. Check `https://YOUR_DOMAIN/healthz`, `/.well-known/oauth-authorization-server`, `/.well-known/oauth-protected-resource` and `/mcp` (401 without access token).
5. Register the MCP endpoint `https://YOUR_DOMAIN/mcp` as a ChatGPT plugin MCP server, choose the discovered OAuth flow, and authorize your REB account in the browser. Do not enter credentials into chat messages. Approval and compatibility depend on ChatGPT's current integration requirements.
6. For local development, `reb-remote serve --host 127.0.0.1 --port 8787` uses local HTTP. **Never expose local HTTP to the internet**.

## Account isolation and controls

Each username is mapped to an isolated SQLite database under `/data/tenants/`. Account, OAuth client, one-use authorization code, and opaque hashed token storage is managed by `/data/remote-identity.sqlite3`. PBKDF2 SHA-256 passwords, OAuth Authorization Code + PKCE S256, opaque 1-hour access and rotating 30-day refresh tokens are implemented. Tokens are never written to project files. External paid operations are disabled remotely unless `REB_REMOTE_ALLOW_EXTERNAL=1` is explicitly configured.

For a multi-tenant production service, have an independent security assessment first: add operator-grade abuse controls and rate limiting, revocation/user deletion, durable backup/restore, observability, consent/privacy policy, data retention and deletion, CSRF defense, quota enforcement, and revocation endpoints. OAuth integration compatibility must be checked against the current host specification. The current server **does not** claim enterprise security certification.

## Real REA / RES

Install REA according to its official docs, then configure its *actual* MCP stdio server command and explicit allowed tools in `examples/nexus-config.example.json` (never pass shell command strings). Run `reb integrations --config /secure/nexus.json` to make a real MCP handshake. No automatic REA download, extraction or bypass.

RES is usually a skill loaded into a compatible external agent, not its own MCP server. Set `REB_RES_SKILLS_DIR` and run `reb integrations`. The Nexus can detect the skill but executing it requires the agent host. Do not claim autonomous RES execution without configuring a host adapter and testing that exact version.

## HubSpot example

Provision a least-privilege private app token with read-only scopes. Set `HUBSPOT_PRIVATE_APP_TOKEN` on the local process (do not commit it or share it). Then `reb hubspot-read contacts --approve-read` reads a small, privacy-redacted record sample. No writes or prospecting messages are performed automatically.

## Live business pilot

Run the planned Business Journey with actual consenting participants, collect recorded experiment outcomes and real revenue/cost data, and compare pre-specified success thresholds. Unit tests or historical case studies cannot prove business success. Consent and GDPR/data-handling review precede a commercial pilot.
