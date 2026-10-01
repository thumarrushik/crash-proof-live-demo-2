# Task: Add started_at timestamp to /health endpoint

Status: in-progress
Date: 2026-09-30
Branch: claude-backend-issue-42

## Problem Statement

Add a `started_at` field to the /health response that contains the ISO-8601 UTC time the process started. This value must be computed once at startup and returned consistently on every request (not regenerated per-call). The field should be in ISO-8601 format ending with 'Z'. Existing fields and tests must remain unchanged. The acceptance criteria require that two calls to /health return the same started_at value, and that a test covers both the existence and consistency of this property.

## Research & Resources

- **app.py, lines 12-13**: STARTED_AT constant already computed at startup using `datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")`
- **app.py, line 49**: started_at field already included in _get_health_status() return dict
- **test_app.py, lines 65-77**: test_health_started_at_is_valid_iso8601() validates ISO-8601 format of started_at
- **test_app.py, lines 555-563**: test_livez_started_at_is_valid_iso8601() validates ISO-8601 for /livez endpoint
- **test_app.py, lines 613-621**: test_readyz_started_at_is_valid_iso8601() validates ISO-8601 for /readyz endpoint
- **test_app.py, lines 219-232**: test_health_response_has_required_nine_fields() - currently validates 9 fields but does NOT include started_at
- **test_app.py, lines 235-252**: test_health_response_field_types() - type checks for 9 fields but NOT started_at

## Assumptions

| # | Ambiguity | Options weighed | Assumed | Why |
|---|-----------|-----------------|---------|-----|
| 1 | Is started_at already implemented? | A) Yes, already in code; B) Need to implement | A | Code inspection shows STARTED_AT constant at app.py:13 and used in response at app.py:49 |
| 2 | What does "test covers both properties" mean? | A) Test field exists + is valid ISO-8601; B) Test field exists + consistency (same value twice); C) Both A and B | B and C | Acceptance criteria say "two calls return the same value" AND "test covers both properties" - suggests a specific test for consistency is needed |
| 3 | Should started_at be in regression test schema? | A) Yes, add to required fields; B) No, separate from current 9; C) Update existing tests | A | Regression tests in 219-252 should validate ALL fields in response, and started_at is now part of the contract |

## Environment Setup

No new packages or services required. Project uses FastAPI and pytest (already in requirements.txt).

## Plan

1. **Verify current implementation** (DONE): Started_at is already computed once at startup and included in responses
2. **Add consistency test**: Create test_health_started_at_consistent_across_calls() that calls /health twice and asserts both return same started_at
3. **Update regression tests**: Add started_at to required fields in test_health_response_has_required_nine_fields() (should be 10 now)
4. **Update type checks**: Add type validation for started_at (must be string, ISO-8601 format ending in Z)
5. **Run full test suite** to ensure no regressions
6. **Verify with both acceptance criteria**:
   - ✓ /health returns started_at as ISO-8601 string ending in Z
   - ✓ Two calls return same value (new test)
   - ✓ Existing fields/tests unchanged (only adding, not modifying existing)
   - ✓ Test covers both properties (consistency test)

## Decisions Made

### Decision: Add new test rather than modify schema tests

- **Context:** Acceptance criteria specifically ask for "a test covers both properties" - started_at exists AND is consistent
- **Options considered:** 
  - Option A: Just verify field type in existing regression tests
  - Option B: Create dedicated consistency test
  - Option C: Do both
- **Chosen:** Option C (both)
- **Why:** Regression tests should validate the full contract (all fields including started_at). But acceptance explicitly calls for testing consistency, so a dedicated test for "same value across calls" is the right complement.

### Decision: Update field count from 9 to 10 in regression tests

- **Context:** Current regression tests check for "required nine fields" but started_at is now part of the contract
- **Options considered:**
  - Option A: Keep as separate test outside regression suite
  - Option B: Update regression tests to include started_at (makes it 10 fields)
  - Option C: Create new regression tier for started_at
- **Chosen:** Option B
- **Why:** Regression tests exist to catch field additions/removals. Started_at is now a required field, so it belongs in the regression validation. This catches accidental removal or type changes.

## Exit Paragraph (Understand phase)

The started_at field is already implemented in the code and returned in all health-check responses (/health, /livez, /readyz). The implementation correctly computes the timestamp once at startup using ISO-8601 format ending with 'Z' and stores it in the STARTED_AT constant. All 56 existing tests pass. However, the test suite is incomplete: there is no test validating that started_at returns the same value on multiple calls (consistency), and the regression test suite does not include started_at in its required-fields validation (still checks for only 9 fields). The work is to add a consistency test and update regression tests to include started_at as a 10th required field, validating both its existence and type.

## Implementation Log

- [ ] Add test_health_started_at_consistent_across_calls()
- [ ] Update test_health_response_has_required_nine_fields() to check for 10 fields including started_at
- [ ] Add type validation for started_at in test_health_response_field_types()
- [ ] Add started_at check in test_health_response_complete_schema_validation()
- [ ] Run pytest to verify all tests pass
- [ ] Verify acceptance criteria met

## Verification Results

(To be filled)

### Failures & Fixes

(None yet)

## Self-review Findings

(To be filled after self-review phase)
