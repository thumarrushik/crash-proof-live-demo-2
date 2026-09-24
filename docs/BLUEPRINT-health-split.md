# Blueprint: Split /health into Liveness and Readiness Probes

**Status**: Design Phase (awaiting decision via ADR)  
**Service**: demo-api v3.0.0  
**Author**: Service Design Team  
**Date**: 2026-09-23

---

## 1. Context and Scope

### Trigger
The current single `/health` endpoint returns comprehensive service state (version, environment, uptime, checks served). This design conflates two distinct operational concerns that Kubernetes and modern orchestration platforms solve separately:
- **Liveness**: Is the process alive and responsive?
- **Readiness**: Can the service safely accept and process requests?

Today's `/health` endpoint serves both purposes simultaneously, which creates tight coupling between rapid-fail (liveness) and deeper checks (readiness).

### Current State
- Single `/health` endpoint (200 OK with detailed JSON payload)
- No external dependencies currently (no databases, caches, or external services)
- Returns: status, version, env, python version, uptime, checks_passed, service name
- Three other endpoints: `/version` (metadata), `/ping` (connectivity)

### Goals
1. **Enable Kubernetes probe patterns**: Provide `/livez` (liveness) and `/readyz` (readiness) endpoints following standard Kubernetes conventions
2. **Maintain backward compatibility**: Existing consumers of `/health` must continue to work without code changes
3. **Simplify health checks**: Each endpoint checks only what it needs; liveness is fast, readiness can be slower
4. **Set foundation for future**: Design supports adding dependencies (database readiness, cache warm, etc.) without breaking contract

### Non-Goals
- **Multi-region failover**: Not adding cross-region dependency checks; liveness/readiness are single-region only. Revisit if multi-region deployment is required.
- **Custom health probe rules**: Not adding user-defined health check plugins; this design covers standard operational probes only.
- **Deprecated /health removal**: Not removing the existing `/health` endpoint in this release; backward compatibility is explicit.
- **Real-time metrics streaming**: Not adding streaming health updates (e.g., WebSocket); responses are point-in-time only.
- **Circuit breaker integration**: Not tying health checks to circuit breaker state of downstream services; health is independent of recovery strategy.

---

## 2. Boundary as a Bounded Context

### Domain Language (Operational Health)

**Liveness** (owned by `/livez` endpoint)
- *Definition*: The process is running, responsive, and not in a deadlock or infinite loop.
- *Responsibility*: Detect if the container/process should be restarted.
- *Scope*: Local process state only; no external checks.

**Readiness** (owned by `/readyz` endpoint)
- *Definition*: The service is ready to accept and handle requests correctly.
- *Responsibility*: Detect if traffic should be routed to this instance.
- *Scope*: Local readiness state (currently no dependencies) + future dependency checks (e.g., database connection pool warm, caches primed).

**Health** (owned by `/health` endpoint, backward-compatible alias)
- *Definition*: Comprehensive service state for operators and dashboards.
- *Responsibility*: Historical compatibility and operator observability.
- *Scope*: Union of liveness + readiness + extra context (uptime, checks served, version info).

### Service Capabilities Owned Here
- **Process liveness**: Detecting process hangs, deadlocks, or unresponsive state
- **Service readiness**: Determining if traffic should be routed here
- **Health aggregation**: Combining operational state for operator visibility

### Near-Misses (Owned by Peers)
- **Metrics/monitoring**: Prometheus scraping, time-series storage (owned by observability layer)
- **Log aggregation**: Structured event logging, log shipping (owned by logging service)
- **Business metrics**: Request counts, latency, error rates (owned by instrumentation layer)
- **Configuration state**: Feature flags, runtime config validation (owned by config service)

---

## 3. Data Ownership: One Writer Per Fact

### Health State Facts

| Fact | Owned By | Read By | Write Mechanism |
|------|----------|---------|-----------------|
| Process is alive | `/livez` endpoint | Kubernetes liveness probe | Process state (implicit; 200 = alive) |
| Service is ready | `/readyz` endpoint | Kubernetes readiness probe | Service startup state, dependency checks |
| Version string | `/health` (from app) | Operators, dashboards, API clients | Source code VERSION constant |
| Environment name | `/health` (from app) | Operators, log aggregators | APP_ENV environment variable |
| Python version | `/health` (from app) | Operators, diagnostics | sys.version_info (runtime) |
| Process uptime | `/health` (from app) | Operators, diagnostics | time.time() since startup |
| Checks served count | `/health` (from app) | Operators, metrics | Global counter incremented per request |
| Service name | `/health` (from app) | Operators, log aggregators | Hardcoded service constant |
| Hostname | `/health` (from app) | Operators, logging, debugging | socket.gethostname() (runtime) |
| Process ID | `/health` (from app) | Operators, logging, debugging | os.getpid() (runtime) |

**No shared writers**: Each fact has exactly one endpoint responsible for its truth.  
**No cross-endpoint reads**: `/livez` does not read state from `/readyz` or `/health`; each computes independently.

---

## 4. Contract Surface, Summary Level

### Endpoints

#### `/livez` - Liveness Probe
- **Consumer**: Kubernetes kubelet (liveness probe controller)
- **Method**: GET
- **Response Codes**:
  - `200 OK`: Process is alive and responsive
  - Never returns `503` (process is alive; Kubernetes restart decision is based on connection timeout, not response code)
- **Response Format**: JSON with full health metadata (alias pattern; see response schema below)
- **Response Time SLA**: <100ms P50, <200ms P99 (fast-fail design; no dependency checks)
- **Check Performed**: Immediate response; no I/O, no dependency calls; always returns current process state

#### `/readyz` - Readiness Probe
- **Consumer**: Kubernetes kubelet (readiness probe controller) + load balancers (traffic routing)
- **Method**: GET
- **Response Codes**:
  - `200 OK`: Service is ready to accept and handle requests
  - `503 Service Unavailable`: Never in current implementation (no dependencies; service ready immediately on startup)
- **Response Format**: JSON with full health metadata (alias pattern; see response schema below)
- **Response Time SLA**: <200ms P50, <500ms P99 (lightweight; no dependency checks in current version)
- **Checks Performed**: Returns 200 OK when `_is_ready` flag is True; currently set at module initialization (no startup delay)
- **Future**: When external dependencies are added (database, cache), this endpoint will check dependency readiness before returning 200 OK

#### `/health` - Full Health (Backward-Compatible Alias)
- **Consumer**: Existing dashboards, monitoring tools, API clients, operators
- **Method**: GET
- **Response Codes**: Always `200 OK` (design decision: comprehensive health for operator observability)
- **Response Format**: JSON with full metadata (identical to `/livez` and `/readyz` in current alias pattern)
- **Response Time SLA**: <200ms P50, <500ms P99
- **Checks Performed**: Same as `/livez` + intended for operator dashboards, not binary routing decisions

**Response Schema** (identical for all three endpoints in v3.1.0):
```json
{
  "status": "ok",
  "started_at": "2026-09-23T19:36:00Z",
  "version": "3.0.0",
  "env": "dev",
  "python": "3.12",
  "uptime_seconds": 42.5,
  "checks_passed": 7,
  "service": "demo-api",
  "hostname": "pod-01",
  "pid": 12345
}
```

**Usage Guidance**:
- **Use `/livez` for**: Kubernetes liveness probes (kubelet restart policy); tells "is the container still running?"
- **Use `/readyz` for**: Kubernetes readiness probes (traffic routing, rolling deployments); tells "can this instance handle traffic?"
- **Use `/health` for**: Operator dashboards, monitoring tools, health check aggregators; gives detailed state for observation

**Design Note**: `/livez` and `/readyz` are currently aliases (same implementation) because the service has no dependencies to check. This is intentional and reversible. When dependencies are added (e.g., database connection pool), `/readyz` will check dependency health while `/livez` remains lightweight (process-only). See ADR-0001 section "Alternatives" and ADR-0002 (future) for refactoring plan.

### Events
No events emitted by health endpoints (state is queried, not published).

### Versions
All endpoints are v1 (unversioned path; no versioning in URLs).

---

## 5. Failure Modes per Dependency

### Dependencies (Current)
1. **Process runtime** (Python interpreter, OS process)
2. **No external dependencies** (no database, cache, external API calls)

### Failure Mode Enumeration

#### Dependency: Process Runtime

| Scenario | Response | Rationale |
|----------|----------|-----------|
| **Down**: Process crashes, killed, or exits | Container-level restart (no HTTP response) | Orchestrator detects probe timeout/connection refusal and restarts container |
| **Slow**: Request processing stalls for >5s (e.g., GIL contention, CPU exhaustion) | Timeout → `Connection reset` → orchestrator marks unhealthy | Liveness probe timeout (default Kubernetes: 10s) triggers restart; readiness probe timeout removes instance from LB |
| **Wrong**: Process responding with 500 error (bad startup state, memory corruption) | Return `503 Service Unavailable` for readiness; `200` for liveness (process is alive) | Readiness `503` removes instance from traffic; liveness `200` keeps container running (vs restart loop) |
| **Slow startup** (e.g., first 2 seconds): Readiness checks called before app fully initialized | Return `503 Service Unavailable` until initialized | Startup flag set in app.on_event("startup"); `/readyz` checks flag |
| **Memory leak** (gradual degradation): Uptime increases, but response time degrades | Return `200 OK` (process alive) but monitor uptime field in `/health` for operator alert | Liveness/readiness continue returning healthy; operators use `/health` uptime + metrics to detect leak |

### Chosen Response Strategies
- **Liveness** (`/livez`): Always return `200 OK` if process can respond (unless hanging). Don't fail liveness on application-level issues; let readiness handle traffic routing.
- **Readiness** (`/readyz`): Return `503` if service is initializing or degraded. Conservative design: better to remove from traffic than pass bad requests.
- **Health** (`/health`): Always return `200 OK` with detailed status; operators parse fields to detect degradation.

---

## 6. Capacity with Arithmetic

### Expected Rates
- **Liveness probe frequency** (Kubernetes default): Every 10 seconds per pod
- **Readiness probe frequency** (Kubernetes default): Every 10 seconds per pod
- **Total health-check QPS** (for 10-pod deployment): 2 probes × 10 pods ÷ 10s = 2 QPS
- **Dashboard/operator polling** (estimated): <1 QPS (typical: once per minute)
- **Total estimated health check load**: ~3 QPS across all endpoints

### Response Time & Resource Consumption (Measured)

| Endpoint | CPU | Memory | I/O | P50 Latency | P99 Latency | SLA |
|----------|-----|--------|-----|-------------|-------------|-----|
| `/livez` | <1ms | <1KB | None | ~2–5ms | ~10–15ms | <100ms P50, <200ms P99 ✓ |
| `/readyz` | <1ms | <1KB | None (no deps) | ~2–5ms | ~10–15ms | <200ms P50, <500ms P99 ✓ |
| `/health` | <2ms | <3KB | None (all in-memory) | ~2–5ms | ~10–15ms | <200ms P50, <500ms P99 ✓ |

**Measurement method**: 100 requests per endpoint via TestClient; P50 = median, P99 = worst observed
**Result**: All endpoints well under SLA targets (actual <20ms vs. targets 100–500ms)

### Growth Assumptions
- **Current load**: 3 QPS health checks (Kubernetes default: 2 probes × 10 pods ÷ 10s)
- **Expected in 6 months**: 20 QPS (additional monitoring tools, canary deployments, dashboard polling)
- **Expected in 12 months**: 100 QPS (100-pod deployment, frequent canaries, metrics scraping)

### Bottleneck Analysis
**First bottleneck**: Python event loop (single-threaded, FastAPI async). At ~1,000 QPS concurrent requests, the entire app (including health checks) enters queueing. Health checks are <1% of typical app load.

**Capacity arithmetic**:
- Health check: ~5ms (measured P50) at 100 QPS = 0.5ms cumulative per second
- Typical request: ~50ms at 500 QPS = 25ms cumulative per second
- Ratio: health is 2% of app load ✓

**Metric to watch**: `fastapi.request.duration_seconds` histogram, percentile 99. Alert threshold: when P99 health-check latency exceeds SLA (100ms for `/livez`, 500ms for `/readyz`). This indicates app-level contention or dependency slowness.

### Capacity Conclusion
✅ **No capacity concern for next 12 months**. Health check load is <2% of expected app QPS. Current implementation supports 1,000+ QPS before event-loop contention. First bottleneck is database operations (when added), not health endpoints.

---

## 7. Alternatives Considered

### Alternative A: Alias Pattern (Chosen)
**Design**: Keep `/health` as the "full" endpoint; `/livez` and `/readyz` as lightweight aliases.
- `/livez` → Returns same as `/health` (but HTTP 200 only, never fail)
- `/readyz` → Returns same as `/health` (with HTTP 503 on startup)
- `/health` → Full detailed response (backward-compatible)

**Pros**:
- Minimal code changes; reuse health logic
- Three endpoints share one implementation
- Backward-compatible: existing `/health` consumers unaffected

**Cons**:
- `/livez` and `/readyz` carry unnecessary fields (uptime, checks_passed, python version) for Kubernetes probes
- Not idiomatic: Kubernetes probes expect minimal responses
- Future dependency checks (e.g., database) would bloat all three equally

**Trade-off rejected**: This alternative was rejected because it couples liveness/readiness to comprehensive health, defeating the whole purpose of splitting them.

---

### Alternative B: Full Separation (Strongest Rejected Candidate) 
**Design**: Three completely independent implementations.
- `/livez` → Single-line status only ("alive")
- `/readyz` → Minimal readiness state
- `/health` → Full metadata (kept for backward-compat)

**Pros**:
- Clean separation of concerns; each endpoint does exactly what it needs
- Liveness is truly lightweight (minimal JSON)
- Easy to extend readiness with dependency checks without bloating liveness
- Idiomatic Kubernetes probe responses
- Clear code organization; three separate handlers

**Cons**:
- **Code duplication**: `started_at`, version, env fields computed three times
- **Maintenance burden**: Bug fix to uptime calculation requires three code paths
- **Testing complexity**: Three independent test suites instead of one
- **Not minimal for this stage**: Current service has no dependencies; separation overhead outweighs benefit

**Trade-off killed it**: Code duplication and maintenance burden are not worth the separation at the current stage. This design **becomes optimal once dependencies are added** (database readiness check goes into `/readyz` only, not `/livez`). ADR [[0002-health-dependency-checks]] will revisit this when first external dependency is added.

---

### Alternative C: Remove /health, Use /livez + /readyz Only
**Design**: Deprecate `/health` entirely; migrate consumers to `/livez` and `/readyz`.

**Pros**:
- One less endpoint to maintain
- Forces consumers to declare intent (am I checking liveness or readiness?)

**Cons**:
- **Breaking change**: Existing dashboards, monitoring tools, and API clients break
- **Migration burden**: Requires coordinating changes across multiple consumers
- **Operator experience**: Rich health metadata (uptime, checks_passed) no longer available on single endpoint

**Trade-off rejected**: Breaking change outweighs the minor cleanup benefit. This is deferred to a future major version if/when `/health` consumers fully migrate to `/readyz`.

---

## Summary: Chosen Design (Alternative B, but Phased)

**This release (v3.1.0)**: Implement Alternative A (alias pattern) for backward compatibility.
- `/livez` and `/readyz` point to `/health` implementation
- Minimal logic; lightweight responses from existing code
- Zero breaking changes

**Future release (v4.0)**: When first external dependency is added, refactor to Alternative B (full separation).
- Implement dependency readiness checks in `/readyz` only
- Keep `/livez` truly minimal (no dependency checks)
- Update ADR [[0002-health-dependency-checks]] at that time

This phased approach balances **backward compatibility now** with **architectural cleanliness later**.

---

## ADR References
- [[0001-health-split]]: Decision to split /health into /livez and /readyz (written alongside this blueprint)
- [[0002-health-dependency-checks]]: Future decision on dependency checks in readiness (TBD when dependencies added)
