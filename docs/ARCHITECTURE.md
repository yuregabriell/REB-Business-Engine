# REB Architecture & contracts

## Control flow

`User -> Host LLM -> reb-core skill -> 14 role catalog -> evidence gate -> tools -> observed results -> project store -> strategy revision`

The host model is responsible for natural-language reasoning. The deterministic engine enforces arithmetic, persistence, schemas and explicit status labels. A tool does not automatically run merely because a skill describes it.

## Evidence record

- `claim`: precisely scoped observable claim.
- `url`: source original; must be HTTP(S) without embedded credentials.
- `status`: verified / inferred / unverified / contradicted.
- `source_type`: original provider or manual observation.
- `collected_at`: UTC collection timestamp.

A recorded URL is not proof the statement is true; verification is a separate human/source review process. Future versions should store source snapshot hashes, authored citations and quality rating.

## Agent contract

Input: `project`, `goal`, `allowed_actions`, `evidence_refs`, `budget`, `current_stage`.

Output: `recommendations`, `assumptions`, `evidence_refs`, `unknowns`, `actions`, `acceptance_criteria`, `risk_register`.

Every action identifies whether it has been proposed, prepared, approved, attempted or observed. No action is reported as completed merely because a text model suggested it.

## Nexus delegation contract

Prepared delegation includes `provider`, `objective`, `evidence_refs`, `approval`, `expected_output`, and `execution_status` (`prepared_not_executed` for `reb delegate`). The optional `reb nexus-call` uses a trusted local `servers` config, tool-level read/write allowlist, explicit approval flags and MCP stdio JSON-RPC requests. Successful calls can produce a non-sensitive receipt, not validated market evidence. REA may be an external MCP tool host, while RES is a skill, not necessarily a separate process. A2A is optional when independent agents implement it. Untrusted skill content is read for discovery and must never be auto-executed.

## Financial model

`contribution = price - variable_cost - customer_acquisition_cost`

`operating_result = units * contribution - period_fixed_cost`

`break_even_units = ceil(fixed_cost / contribution)` when contribution > 0.

Assumptions: one service, one period, fixed per-unit customer acquisition cost. Excludes taxes, capex depreciation and time-varying demand. Expanding the model requires explicit variables and regression tests.

## Memory

SQLite is local single-user and not an authenticated hosted storage layer. For multi-user SaaS migrate to a secured DB, encrypted backups, tenant isolation, deletion policies and secret management.
