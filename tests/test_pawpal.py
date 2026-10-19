import sys
from pathlib import Path

# pawpal_system.py lives in diagrams/, so make it importable from tests/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "diagrams"))

from pawpal_system import Pet, Priority, Task


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
