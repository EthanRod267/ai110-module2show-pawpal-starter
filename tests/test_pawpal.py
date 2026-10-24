import sys
from pathlib import Path

# pawpal_system.py lives in diagrams/, so make it importable from tests/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "diagrams"))

from datetime import date, time, timedelta

from pawpal_system import DailySchedule, Owner, Pet, Priority, Task, TimeWindow


def test_mark_complete_changes_status():
    task = Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task(title="Feed", duration_minutes=10, priority=Priority.MEDIUM))

    assert len(pet.tasks) == 1


def test_filter_tasks_by_status_and_pet():
    owner = Owner("Jordan", available_minutes=60)
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    walk = Task("Walk", 30, Priority.HIGH)
    feed = Task("Feed", 10, Priority.HIGH)
    meds = Task("Meds", 5, Priority.HIGH)
    mochi.add_task(walk)
    mochi.add_task(feed)
    luna.add_task(meds)
    walk.mark_complete()

    assert owner.filter_tasks() == [walk, feed, meds]
    assert owner.filter_tasks(completed=True) == [walk]
    assert owner.filter_tasks(completed=False) == [feed, meds]
    assert owner.filter_tasks(pet_name="mochi") == [walk, feed]
    assert owner.filter_tasks(completed=False, pet_name="Mochi") == [feed]
    assert owner.filter_tasks(pet_name="Rex") == []


def test_task_not_due_before_next_due_date():
    owner = Owner("Jordan", available_minutes=60)
    luna = Pet("Luna", "cat")
    owner.add_pet(luna)
    brushing = Task("Brushing", 15, Priority.MEDIUM, frequency="weekly")
    luna.add_task(brushing)
    today = date.today()
    brushing.next_due = today + timedelta(days=7)

    schedule = DailySchedule(today, owner)
    schedule.generate_plan(day_start=time(7, 0))
    assert schedule.items == []

    later = DailySchedule(today + timedelta(days=7), owner)
    later.generate_plan(day_start=time(7, 0))
    assert [i.task for i in later.items] == [brushing]


def test_task_past_midnight_is_skipped_not_wrapped():
    owner = Owner("Jordan", available_minutes=120)
    mochi = Pet("Mochi", "dog")
    owner.add_pet(mochi)
    walk = Task("Late walk", 30, Priority.HIGH, time_window=TimeWindow(time(23, 45)))
    mochi.add_task(walk)

    schedule = DailySchedule(date.today(), owner)
    schedule.generate_plan(day_start=time(7, 0))

    assert schedule.items == []
    assert schedule.skipped == [(walk, "would run past midnight")]
