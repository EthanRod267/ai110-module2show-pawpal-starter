# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

==================================================
Today's Schedule
==================================================
Plan for Jordan on Monday, Oct 19:
  [ ] 07:00-07:30  Morning walk (Mochi, 30 min) [HIGH]
  [ ] 07:30-07:40  Breakfast (Mochi, 10 min) [HIGH]
  [ ] 08:00-08:05  Thyroid meds (Luna, 5 min) [HIGH]
  [ ] 12:00-12:15  Brushing (Luna, 15 min) [MEDIUM]
  [ ] 16:00-16:20  Fetch in the yard (Mochi, 20 min) [LOW]
  [ ] 18:00-18:10  Litter box cleaning (Luna, 10 min) [MEDIUM]
  Time used: 90/120 min

Why this plan:
  - Morning walk at 07:00: high priority, earliest allowed start is 07:00
  - Breakfast at 07:30: high priority, earliest allowed start is 07:30
  - Thyroid meds at 08:00: high priority, earliest allowed start is 08:00
  - Brushing at 12:00: medium priority, earliest allowed start is 12:00
  - Fetch in the yard at 16:00: low priority, earliest allowed start is 16:00
  - Litter box cleaning at 18:00: medium priority, earliest allowed start is 18:00
```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

All scheduling logic lives in `diagrams/pawpal_system.py`. The scheduler class is `DailySchedule`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `DailySchedule.sort_by_time()` | Orders tasks by the earliest start in their time window; tasks with no time go last |
| Filtering | `Owner.filter_tasks(completed=..., pet_name=...)` | Filter by completion status, pet name, or both |
| Conflict handling | `DailySchedule.generate_plan()` | Skips tasks that can't fit, can't finish in their window, or would run past midnight, and records why |
| Recurring tasks | `Task.mark_complete()`, `Task.is_due()` | Daily and weekly tasks get a next due date; tasks that aren't due yet are left off the plan |

### Sorting: `DailySchedule.sort_by_time(tasks=None)`

- Sorts tasks by `task.earliest`, the earliest allowed start in the task's time window.
- Tasks with no time window go at the end of the list.
- Returns a new list and leaves the original unchanged. Tasks with the same start time keep their original order.
- If you don't pass a list, it sorts every task the owner has. You can also pass in a filtered list:
  `schedule.sort_by_time(owner.filter_tasks(completed=False))`.

### Filtering: `Owner.filter_tasks(completed=None, pet_name=None)`

- `completed=True` returns finished tasks, `completed=False` returns unfinished ones, and `None` returns both.
- `pet_name` limits the results to one pet. The match ignores capitalization, so `"mochi"` finds `"Mochi"`.
- The two filters can be combined, for example `owner.filter_tasks(completed=False, pet_name="Luna")`.
- With no arguments, it returns every task across all pets.

### Conflict handling: `DailySchedule.generate_plan(day_start)`

`generate_plan()` builds the plan in three steps:

1. **Retrieve:** collect every pet's unfinished tasks that are due today.
2. **Select:** take tasks in priority order (HIGH first, shorter tasks first on ties) until the owner's `available_minutes` runs out.
3. **Order:** move a time cursor forward from `day_start`. At each free slot, run the highest-priority task whose time window has opened. A heap (`heapq`) holds the ready tasks so the scheduler never has to rescan the whole list.

Two tasks are never booked at the same time, because each task starts when the previous one ends. When a task can't be placed, it is skipped instead of crashing the program. Each skip is recorded in `schedule.skipped` with one of these reasons:

- `not enough time left (N min remaining)`: the time budget is used up.
- `could not finish before HH:MM`: the task would run past the end of its time window.
- `would run past midnight`: the task would end after 24:00.

`explain_reasoning()` prints these reasons next to the scheduled tasks.

### Recurring tasks: `Task.mark_complete()` and `Task.is_due(day)`

- Each task has a `frequency` of `"daily"` or `"weekly"`.
- `mark_complete()` sets `next_due` to tomorrow for a daily task, or one week from today for a weekly task.
- `is_due(day)` returns `True` when the task has no `next_due` date or when `day` is on or after `next_due`. `generate_plan()` leaves out tasks that aren't due.
- **Known limitation:** `mark_complete()` also sets `completed = True`, and `generate_plan()` skips completed tasks. As a result, a recurring task won't reappear on its next due date until `mark_incomplete()` is called.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

## Implementation Summary
Priority: Enum for task priority levels.
TimeWindow: Represents the earliest start and latest end times for a task.
Task: Represents a task with details, time window, and completion status.
Pet: Represents a pet with its details and associated tasks.
Owner: Represents the pet owner with their details, preferences, and pets.
ScheduledItem: Represents a task scheduled at a specific time with a reason.

