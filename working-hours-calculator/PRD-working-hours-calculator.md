# Product Requirements Document (PRD)

## 1. Product Overview

A web app that helps employees design and compare 2-week working patterns.  
For each pattern, the app calculates daily hours, weekly totals, fortnight totals, and the gap versus contracted hours.  
This replaces a spreadsheet.

---

## 2. Goals & Success Criteria

Goals:
- Allow users to configure their contract (weekly hours, fortnight hours, default break length).
- Allow multiple 2-week working pattern “rows”.
- Show totals and gap instantly as times change.

Success Criteria:
- Settings persist.
- User can create, edit, duplicate, and compare multiple patterns.
- Calculations match spreadsheet logic exactly.

---

## 3. Users & Use Cases

Primary user: an employee working flexi or part-time patterns.

Examples:
- Designing a flexi pattern that creates alternate Fridays off.
- Creating a 90% pattern with early finish on Fridays.
- Comparing multiple patterns to find one that hits contracted hours.

---

## 4. Settings

Global settings used by all patterns.

### 4.1 Contract Settings

- Hours per week (example: 37.5).
- Cycle length: two weeks (fixed for v1).
- Target hours per fortnight:
  Calculated as hours_per_week × 2, but user may override manually.

### 4.2 Break Settings

- Default break length in minutes (example: 60).
- Each day in each pattern can override its break length.

In v1, all breaks are manually editable per day but prefilled using the default break.

---

## 5. Patterns (Rows)

A pattern represents one 2-week schedule.

### 5.1 Pattern Structure

Each pattern has:
- A name (example: “Flexi Friday Off”).
- Ten days: Week 1 (Mon–Fri) and Week 2 (Mon–Fri).
- Each day stores:
  - Start time (HH:MM).
  - End time (HH:MM).
  - Break length in minutes.
  - A derived value for daily working hours.

---

## 6. Calculations

### 6.1 Daily Hours

Daily hours = (end_time minus start_time minus break_minutes) expressed in decimal hours.

Example:
If someone works 08:30 to 17:30 with a 60-minute break:  
Raw minutes = 540  
Work minutes = 480  
Daily hours = 8.00

### 6.2 Weekly Totals

Hours Week 1 = sum of daily hours for Monday–Friday of Week 1.  
Hours Week 2 = sum of daily hours for Monday–Friday of Week 2.

### 6.3 Fortnight Total

Fortnight hours = Week 1 hours + Week 2 hours.

### 6.4 Gap vs Contract

Gap = fortnight_hours minus target_fortnight_hours.

Display:
- Zero means perfect alignment.
- Positive means over target.
- Negative means under target.
- Colour coding recommended.

---

## 7. Features

### 7.1 Pattern Management

- Add pattern (prefilled with default times or empty).
- Rename pattern.
- Duplicate pattern.
- Delete pattern.

### 7.2 Pattern Editor

Each pattern shows:
- Name field.
- Ten editable day entries (start, end, break).
- Read-only display of daily hours.
- Summary row displaying:
  - Hours Week 1
  - Hours Week 2
  - Fortnight total
  - Gap vs contract

Calculations update instantly.

### 7.3 Comparison View

A compact list showing all patterns:
- Name
- Week 1 hours
- Week 2 hours
- Fortnight hours
- Gap

Highlight the pattern closest to a zero gap.

---

## 8. Validation

- End time must be after start time.
- Break minutes must be non-negative and less than the total working duration.
- Invalid daily entries show no hours and are excluded from totals.
- Pattern shows a clear error indicator if any invalid days exist.

---

## 9. Non-Goals (v1)

- No multi-user accounts.
- No HR/payroll integration.
- No weekends.
- No syncing to calendars.

---

## 10. Implementation Notes

- A small SPA built with React, Vue, Svelte, or similar.
- Data stored in localStorage for v1.
- A helper function for time arithmetic to avoid rounding issues.

---

## 11. Acceptance Criteria

- A standard 37.5-hour pattern produces 7.5 hours/day, 37.5 per week, and 75 per fortnight.
- A Week-2-Friday-off pattern totals exactly 75 hours when designed accordingly.
- Editing any start/end/break immediately updates all totals.
- User can reliably add, duplicate, rename, and delete patterns without refreshing.

