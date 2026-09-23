# Task Report

## What was built

Resolved merge conflict in PR #27 by combining two independent features from branches claude/issue-20 and main. The /health endpoint now returns both the `service: "demo-api"` field (from claude/issue-20) and the `checks_passed` counter that increments with each call (from main). All 11 tests pass, covering both features and existing functionality. The resolution preserves the intent of both branches without clobbering either side.

## How it was verified

Merged origin/main into claude/issue-20, resolved all conflict markers in app.py and test_app.py, then ran the full test suite.

Command: `git merge origin/main --no-commit --no-ff`
Result: Auto-merging app.py and test_app.py, both with content conflicts

Resolved conflicts by:
1. Keeping the global `_checks_passed` counter and increment logic from main
2. Keeping the `service: "demo-api"` field from claude/issue-20
3. Combining all tests from both branches

Command: `python3 -m pytest test_app.py -v`
```
test_app.py::test_health_returns_200 PASSED                              [  9%]
test_app.py::test_health_returns_ok_status PASSED                        [ 18%]
test_app.py::test_version_returns_200 PASSED                             [ 27%]
test_app.py::test_version_returns_correct_version PASSED                 [ 36%]
test_app.py::test_ping_returns_200 PASSED                                [ 45%]
test_app.py::test_ping_returns_pong PASSED                               [ 54%]
test_app.py::test_health_version_equals_version_endpoint PASSED          [ 63%]
test_app.py::test_health_includes_checks_passed PASSED                   [ 72%]
test_app.py::test_checks_passed_increments_across_calls PASSED           [ 81%]
test_app.py::test_health_service_field_present PASSED                    [ 90%]
test_app.py::test_health_service_field_equals_demo_api PASSED            [100%]

11 passed, 1 warning in 0.62s
```

Exit code: 0 (success)

## Files

- app.py (modified) — Added `_checks_passed` counter; health endpoint returns all fields
- test_app.py (modified) — Combined tests for both `checks_passed` and `service` features
- REPORT.md (created) — This report

## Noticed, not changed

None.
