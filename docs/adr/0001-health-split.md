# ADR-0001: Split /health into /livez and /readyz probes

**Status**: Accepted (2026-09-23)

## Context

The current `/health` endpoint returns comprehensive service state: status, version, environment, Python version, uptime, checks served, and service name. This design conflates two distinct operational concerns that Kubernetes and modern orchestrators solve separately:

- **Liveness**: Is the process alive and responsive? (used by container restart policies)
- **Readiness**: Is the service ready to accept traffic? (used by load balancers and traffic routing)

Today's single endpoint serves both purposes simultaneously, creating implicit coupling between rapid-fail checks (liveness) and deeper introspection (readiness). Kubernetes probes expect minimal, fast responses; returning comprehensive metadata on every liveness check is not idiomatic. Additionally, once external dependencies are added (database, cache, external APIs), readiness checks will need to include dependency health, while liveness should remain lightweight—a split enables this without affecting current code.

The service currently has no external dependencies, so the separation overhead must be weighed against the clarity gain.

## Decision

We will provide `/livez` (liveness) and `/readyz` (readiness) endpoints following Kubernetes probe conventions, implemented as lightweight aliases to the existing `/health` endpoint for v3.1.0. The `/health` endpoint remains unchanged for backward compatibility.

## Consequences

**Easier:**
- Kubernetes deployments can use idiomatic probe paths (`/livez` for liveness policy, `/readyz` for readiness policy)
- Foundation is laid for future readiness checks on external dependencies without breaking liveness
- Existing `/health` consumers continue working without modification

**Harder:**
- `/livez` and `/readyz` responses include unnecessary fields (uptime, checks_passed, full metadata) that Kubernetes probes don't need; this is wasted JSON payload
- Three endpoint paths now exist for similar concerns, creating documentation burden
- Refactoring to full separation (when dependencies are added) will require code changes in `/readyz` only, but requires careful testing

**New problems created:**
- Temporary architectural debt: this alias pattern will need refactoring once a dependency is added; the right pattern (full separation) is deferred, requiring future rework
- Documentation must clarify that `/livez` and `/readyz` are presently aliases, not independent implementations

## Alternatives

**Keep single `/health` endpoint** — rejected: blocks standard Kubernetes probe patterns and doesn't split architectural concerns. Teams must either use `/health` for both probes (non-idiomatic) or implement custom probe wrappers.

**Full separation (independent `/livez`, `/readyz`, `/health` implementations)** — rejected: introduces code duplication for version, environment, started_at fields. Maintenance burden (fixing uptime calculation three times) outweighs clarity gain at the current stage with no dependencies. This becomes optimal once the first external dependency is added; see ADR-0002 (future) for refactoring trigger.

**Deprecate `/health`, migrate all consumers to `/livez` and `/readyz`** — rejected: breaking change. Existing dashboards, monitoring tools, and API clients depend on `/health`; migration requires coordinating changes across multiple consumers. Deferred to a future major version.

## Implementation Notes

- Status codes: `/livez` returns `200 OK` when alive (never `503` unless process has crashed). `/readyz` returns `200 OK` when ready, `503 Service Unavailable` during startup or if initialization fails.
- All three endpoints (`/livez`, `/readyz`, `/health`) are GET-only, stateless, and require no authentication (standard for health probes).
- See [docs/BLUEPRINT-health-split.md](../BLUEPRINT-health-split.md) for full design including failure modes, capacity analysis, and binding alternatives.

---

**Superseded by**: (none yet)  
**See also**: ADR-0002 (future): Full separation when first external dependency is added
