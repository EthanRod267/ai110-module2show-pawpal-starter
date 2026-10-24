from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from datetime import date as Date, datetime, time as Time, timedelta
from enum import IntEnum
from uuid import uuid4


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
# TimeWindow is the earliest start and latest end for a task.
class TimeWindow:
    earliest: Time | None = None
    latest: Time | None = None


@dataclass
# Task class represents a task with a unique id, duration, priority, frequency, optional time window, completion status, and its pet.
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    frequency: str = "daily"
    time_window: TimeWindow | None = None
    completed: bool = False
    pet: Pet | None = None
    id: str = field(default_factory=lambda: uuid4().hex)
    next_due: Date | None = None

    @property
    def earliest(self) -> Time | None:
        """Earliest allowed start, or None if the task has no window."""
        return self.time_window.earliest if self.time_window else None

    @property
    def latest(self) -> Time | None:
        """Latest allowed end, or None if the task has no window."""
        return self.time_window.latest if self.time_window else None

    def is_due(self, day: Date) -> bool:
        """Return True if this task should appear on the given day.

        A task with no next_due date is always due. Otherwise it becomes due
        again on or after next_due (set by mark_complete for recurring tasks).

        Args:
            day: The date being scheduled.
        """
        return self.next_due is None or day >= self.next_due

    def edit(
        self,
        title: str | None = None,
        duration_minutes: int | None = None,
        priority: Priority | None = None,
        time_window: TimeWindow | None = None,
        frequency: str | None = None,
    ) -> None:
        """Update any provided fields, validating duration and priority."""
        if title is not None:
            self.title = title
        if duration_minutes is not None:
            if duration_minutes <= 0:
                raise ValueError("duration_minutes must be positive")
            self.duration_minutes = duration_minutes
        if priority is not None:
            self.priority = Priority(priority)
        if time_window is not None:
            self.time_window = time_window
        if frequency is not None:
            self.frequency = frequency

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True
        # set next due date (today + 1 day, or + 7 days for weekly instead of a permanent flag)
        if self.frequency == "daily":
            self.next_due = datetime.now().date() + timedelta(days=1)
        elif self.frequency == "weekly":
            self.next_due = datetime.now().date() + timedelta(days=7)

    def mark_incomplete(self) -> None:
        """Mark this task as not done."""
        self.completed = False


@dataclass
# Pet class represents a pet with its details and associated tasks.
class Pet:
    name: str
    species: str
    age: int = 0
    special_needs: str = ""
    tasks: list[Task] = field(default_factory=list)

    def set_info(
        self, name: str, species: str, age: int, special_needs: str
    ) -> None:
        """Replace this pet's basic details."""
        self.name = name
        self.species = species
        self.age = age
        self.special_needs = special_needs

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and link it back to the pet."""
        # Link the task back to this pet so the scheduler knows whose task it is.
        task.pet = self
        self.tasks.append(task)

    def get_task(self, task_id: str) -> Task:
        """Return the task with the given id, or raise KeyError."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise KeyError(f"No task with id {task_id} for {self.name}")

    def edit_task(self, task_id: str, updates: dict) -> None:
        """Apply a dict of field updates to the task with the given id."""
        self.get_task(task_id).edit(**updates)

    def remove_task(self, task_id: str) -> None:
        """Detach the task with the given id from this pet."""
        task = self.get_task(task_id)
        self.tasks.remove(task)
        task.pet = None


@dataclass
# Owner class represents the pet owner with their details, preferences, and associated pets.
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def set_info(
        self, name: str, available_minutes: int, preferences: list[str]
    ) -> None:
        """Replace the owner's basic details and preferences."""
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        # Flatten every pet's task list into one list; this is the scheduler's single entry point.
        return [task for pet in self.pets for task in pet.tasks]

    def filter_tasks(
        self, completed: bool | None = None, pet_name: str | None = None
    ) -> list[Task]:
        """Return tasks matching the given completion status and/or pet name.

        Each filter left as None is not applied, so filter_tasks() returns every
        task. Pet names match case-insensitively; tasks with no pet never match
        a pet_name filter. Tasks keep their original pet-then-insertion order.

        Args:
            completed: True for finished tasks, False for unfinished, None for both.
            pet_name: Only include tasks belonging to the pet with this name.
        """
        # None means "don't filter on this"; pet names match case-insensitively.
        return [
            task
            for task in self.get_all_tasks()
            if (completed is None or task.completed == completed)
            and (
                pet_name is None
                or (task.pet is not None and task.pet.name.lower() == pet_name.lower())
            )
        ]


@dataclass
# ScheduledItem is a task placed at a start/end time, with its reason and per-day completion.
class ScheduledItem:
    task: Task
    start_time: Time
    end_time: Time
    reason: str = ""
    completed: bool = False


MINUTES_PER_DAY = 24 * 60


def _to_minutes(t: Time) -> int:
    """Return t as minutes since midnight."""
    return t.hour * 60 + t.minute


def _to_time(minutes: int) -> Time:
    """Return minutes since midnight as a time (must be within the day)."""
    return Time(minutes // 60, minutes % 60)


@dataclass
# DailySchedule is the plan for one date; the time budget comes from the owner (single source of truth).
class DailySchedule:
    date: Date
    owner: Owner
    items: list[ScheduledItem] = field(default_factory=list)
    skipped: list[tuple[Task, str]] = field(default_factory=list)

    @property
    def time_budget(self) -> int:
        """Minutes available for the day, taken from the owner."""
        return self.owner.available_minutes

    def generate_plan(self, day_start: Time) -> None:
        """Build the day's schedule starting at day_start, recording skipped tasks.

        Runs in three steps:
          1. Retrieve: every pet's unfinished tasks that are due on self.date.
          2. Select: greedily take tasks by highest priority (shorter first on
             ties) until the owner's time budget runs out.
          3. Order: walk a time cursor forward from day_start; at each free slot,
             run the highest-priority task whose window has opened (a heap keeps
             this O(n log n)). If nothing is ready, jump to the next window.

        Tasks that don't fit the budget, can't finish before their window's
        latest time, or would run past midnight are added to self.skipped with
        a reason. Replaces any previous self.items and self.skipped.

        Args:
            day_start: The earliest time any task may begin.
        """
        self.items = []
        self.skipped = []

        # 1. Retrieve: every pet's unfinished tasks that are due on this date.
        pending = [
            t for t in self.owner.get_all_tasks()
            if not t.completed and t.is_due(self.date)
        ]

        # 2. Select: highest priority first, shorter tasks break ties, until the budget runs out.
        by_priority = sorted(pending, key=lambda t: (-t.priority, t.duration_minutes))
        selected: list[Task] = []
        minutes_left = self.time_budget
        for task in by_priority:
            if task.duration_minutes <= minutes_left:
                selected.append(task)
                minutes_left -= task.duration_minutes
            else:
                self.skipped.append(
                    (task, f"not enough time left ({minutes_left} min remaining)")
                )

        # 3. Order: at each free slot, run the highest-priority task whose window has opened.
        # Work in minutes since midnight; convert back to Time only for ScheduledItem.
        start_min = _to_minutes(day_start)

        def opens_at(t: Task) -> int:
            """Minute the task may start: its window's earliest, but never before day_start."""
            return max(_to_minutes(t.earliest), start_min) if t.earliest else start_min

        upcoming = sorted(selected, key=opens_at)
        # Heap of tasks whose window has opened; the index breaks ties so Tasks are never compared.
        ready: list[tuple[int, int, int, Task]] = []
        cursor, i = start_min, 0
        while i < len(upcoming) or ready:
            if not ready:
                cursor = max(cursor, opens_at(upcoming[i]))
            while i < len(upcoming) and opens_at(upcoming[i]) <= cursor:
                t = upcoming[i]
                heapq.heappush(ready, (-t.priority, t.duration_minutes, i, t))
                i += 1
            task = heapq.heappop(ready)[-1]
            end = cursor + task.duration_minutes
            if task.latest and end > _to_minutes(task.latest):
                self.skipped.append((task, f"could not finish before {task.latest:%H:%M}"))
                continue
            if end >= MINUTES_PER_DAY:
                self.skipped.append((task, "would run past midnight"))
                continue
            start = _to_time(cursor)
            self.items.append(
                ScheduledItem(task, start, _to_time(end), reason=self._reason_for(task, start))
            )
            cursor = end

    def _reason_for(self, task: Task, start: Time) -> str:
        """Explain why a task was scheduled at the given start time."""
        reason = f"{task.priority.name.lower()} priority"
        if task.earliest and start == task.earliest:
            reason += f", earliest allowed start is {task.earliest:%H:%M}"
        return reason

    def display_plan(self) -> str:
        """Return the schedule as a readable multi-line string."""
        if not self.items:
            return f"No tasks scheduled for {self.date:%A, %b %d}."
        lines = [f"Plan for {self.owner.name} on {self.date:%A, %b %d}:"]
        for item in self.items:
            pet = item.task.pet.name if item.task.pet else "unassigned"
            check = "x" if item.completed or item.task.completed else " "
            lines.append(
                f"  [{check}] {item.start_time:%H:%M}-{item.end_time:%H:%M}  "
                f"{item.task.title} ({pet}, {item.task.duration_minutes} min) "
                f"[{item.task.priority.name}]"
            )
        used = sum(i.task.duration_minutes for i in self.items)
        lines.append(f"  Time used: {used}/{self.time_budget} min")
        return "\n".join(lines)

    def explain_reasoning(self) -> str:
        """Return why each task was scheduled or skipped."""
        lines = ["Why this plan:"]
        for item in self.items:
            lines.append(
                f"  - {item.task.title} at {item.start_time:%H:%M}: {item.reason}"
            )
        for task, why in self.skipped:
            lines.append(f"  - Skipped {task.title}: {why}")
        if len(lines) == 1:
            lines.append("  - No tasks to schedule.")
        return "\n".join(lines)

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks ordered by earliest allowed start; tasks with no time go last.

        Returns a new list and leaves the input unchanged. The sort is stable,
        so tasks with the same start (or no start) keep their original order.

        Args:
            tasks: Tasks to sort; defaults to every task the owner has.
        """
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        # Untimed tasks (True) sort after timed ones (False); Time.max avoids comparing None.
        return sorted(tasks, key=lambda t: (t.earliest is None, t.earliest or Time.max))
