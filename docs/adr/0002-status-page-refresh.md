# ADR 0002: Status Page Refresh and Last-Checked Timestamp

## Status
In Progress

## Context
The status page at `/` fetches `/health` on page load but provides no indication of when the data was fetched. Users cannot manually refresh the data to check for updates.

GitHub Issue #38 requires:
1. Display a 'last checked' timestamp in human-readable format
2. Add a 'Refresh' button to manually re-fetch `/health`
3. Button disabled during fetch (loading state)
4. Failed fetch shows error without clearing previous good data
5. All four render states (loading, empty, error, data) must be covered
6. Existing tests must keep passing

## Assumptions
| What | Options | Chosen | Why |
|------|---------|--------|-----|
| Time format | ISO-8601, relative ("2 mins ago"), human-readable | Human-readable (e.g., "Last checked: 2:45:30 PM UTC") | Most accessible for a status page |
| Button placement | Top, bottom, inline with title | Next to title as part of header | Intuitive, always visible |
| Loading indicator | Spinner, text, button state | Disabled button + disable refresh action during fetch | Minimal changes to existing HTML |
| Error recovery | Hide error after 5s, require click to dismiss | Keep error visible until next successful fetch | Safe - user knows what failed |
| Initial state | "Never checked", "Checking...", empty list | Empty list with "Loading..." | Matches current behavior |

## Design
### Files to Modify
- `app.py`: Update the HTML response for `/` to include JavaScript for handling refresh logic

### Component Structure
The status page will:
1. Show initial loading state on page load
2. Fetch `/health` and display results with "Last checked: HH:MM:SS UTC"
3. Display Refresh button that:
   - Fetches `/health` again on click
   - Is disabled during the fetch (loading state)
   - Shows loading state during fetch
4. If fetch fails:
   - Show error message at top
   - Keep previous good data visible
   - Enable refresh button for retry

### Render States
1. **Loading (initial)**: "Loading..." message, no button state changes
2. **Data**: Health data list + "Last checked" timestamp + enabled Refresh button
3. **Error**: Error message + previous data list (if any) + enabled Refresh button
4. **Empty**: Should not occur with this API, but handle gracefully

### Data Flow
```
Page Load
  ↓
Fetch /health
  ↓ (success)
Display data + timestamp + enable button
  ↓ (failure)
Show error, keep previous data, enable button
  ↓
User clicks Refresh
  ↓
Disable button + show loading state
  ↓
Fetch /health (same as above)
```

## Implementation Strategy
1. Modify the HTML in `app.py` root() function
2. Add JavaScript to handle:
   - Initial fetch on page load
   - Refresh button click handler
   - Button disabled state management
   - Timestamp formatting in local time or UTC
   - Error display without clearing previous data
3. No backend changes needed (existing `/health` endpoint is sufficient)

## Decisions
- Will use `new Date()` for timestamp formatting (human-readable in browser's locale)
- Refresh button placed next to heading for prominence
- Error message shown in red text at top
- Button disabled state controlled via `disabled` attribute
- All state managed in client-side JavaScript (no backend state needed)

## Verification Plan
- Unit tests (if applicable) for timestamp logic
- Browser tests for all four render states:
  - Loading on initial page load
  - Data displayed with timestamp and enabled button
  - Error shown with previous data intact
  - Refresh button re-fetches and updates timestamp
- Existing tests must continue to pass

## Status Tracking
- [ ] Understand: ADR created, requirements understood
- [ ] Design: UI/UX reviewed (design-ui skill)
- [ ] Implement: Changes made to app.py
- [ ] Verify: Tests pass, browser behavior verified
- [ ] Self-review: Code reviewed, markdown synced
- [ ] Report: REPORT.md created, delivered

