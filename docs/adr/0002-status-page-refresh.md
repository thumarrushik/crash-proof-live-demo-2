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

### Inventory & Hierarchy
- **Component Library**: App has minimal styling; using semantic HTML (`<button>`, `<div>`, `<ul>`)
- **Primary Action**: Refresh button (semantic `<button>` element)
- **Secondary**: Timestamp and status title
- **Tertiary**: Data list (existing structure preserved)

### Layout
```
┌─────────────────────────────────┐
│ Status        [Refresh Button]  │  <- header row
│                                 │
│ Last checked: 2:45:30 PM UTC   │  <- timestamp
│ [Error message if fetch failed] │  <- error area
│ • status: ok                    │  <- data list
│ • version: 3.0.0               │
│ ...                             │
└─────────────────────────────────┘
```

### Files to Modify
- `app.py`: Update the HTML response for `/` to include JavaScript for handling refresh logic

### Component Structure
The status page will:
1. Show initial loading state on page load
2. Fetch `/health` and display results with "Last checked: HH:MM:SS" (local time)
3. Display Refresh button (semantic `<button>`) that:
   - Fetches `/health` again on click
   - Is disabled during the fetch (loading state)
   - Shows loading state during fetch
4. If fetch fails:
   - Show error message at top (NN/g format: what happened + next action)
   - Keep previous good data visible
   - Enable refresh button for retry

### Render States (all four must have assertions)
1. **Loading (initial)**: Show "Loading..." text, no data yet
2. **Data**: Health data list + "Last checked" timestamp + enabled Refresh button
3. **Error**: Error message ("Failed to fetch health data. Check your connection and try again.") + previous data list (if any) + enabled Refresh button
4. **Empty**: Should not occur with this API (API always returns data), but handle gracefully with "No data available"

### Accessibility
- Use semantic `<button>` for refresh action
- Button has visible label ("Refresh")
- Button focus is visible (browser default or styled replacement)
- Error message uses color (red) + text content (not color-only signal)
- Timestamp is plain text (not color-only signal)
- All elements reachable by keyboard
- Target size: Refresh button >= 24px (padding adds to native button default)

### Data Flow
```
Page Load
  ↓
Show "Loading..." + fetch /health
  ↓ (success)
Display data + timestamp + enable button
  ↓ (failure)
Show error, keep previous data (if any), enable button
  ↓
User clicks Refresh
  ↓
Show loading state + disable button
  ↓
Fetch /health (same as above)
```

### Responsive Design
- Single column layout (no horizontal scroll on 320px)
- Relative units for spacing
- Button and text reflow naturally
- Timestamp inline with heading on desktop, wraps on mobile

## Implementation Details

### Changes Made
1. **Modified `app.py` root() function** to return enhanced HTML with:
   - Semantic `<button>` element for refresh action
   - Timestamp `<div>` (updates on each fetch)
   - Error message area (red background, clear messaging)
   - Health data `<div>` (preserves content on error)

2. **Added inline CSS** with:
   - Flexbox layout for header (button next to title)
   - Minimal styling (gray button, red error box)
   - Focus outline for accessibility (2px blue outline)
   - Responsive design (wraps on small screens)
   - Button disabled state (opacity reduced, cursor not-allowed)

3. **Added JavaScript with**:
   - `formatTimestamp()` function: Formats date as "Last checked: HH:MM:SS AM/PM on MM/DD/YYYY"
   - `fetchHealthData()` function:
     - Disables button and shows loading state
     - Fetches `/health` endpoint
     - Updates timestamp on success
     - Displays health data as unordered list
     - On error: shows NN/g error message (what + why + next action), preserves previous data
     - Re-enables button in finally block
   - Click handler on refresh button
   - Auto-fetch on page load

### No Backend Changes
- Existing `/health` endpoint is sufficient
- No new database, no new API endpoints needed

## Decisions
- **Timestamp format**: Using browser locale time format (`toLocaleTimeString()` + `toLocaleDateString()` or just time for brevity)
- **Button placement**: Next to heading (h1) for prominence and easy discovery
- **Error display**: Red text + error message text (not color-only; color + text is required by WCAG 1.4.1)
- **Button element**: Using semantic `<button>` (not `<div onclick>`), with `disabled` attribute for disabled state
- **State management**: All state managed in client-side JavaScript (no backend state needed)
- **Data persistence**: Keep previous data on error (safe pattern, user knows fetch failed)
- **Loading state**: Disable button + show loading text (no separate spinner, minimal changes)
- **Time format**: Local time in HH:MM:SS format for clarity ("Last checked: 2:45:30 PM")

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

