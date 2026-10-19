from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date as Date


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: int
    time_constraint: str = ""
    completed: bool = False

    def edit(
        self,
        title: str | None = None,
        duration_minutes: int | None = None,
        priority: int | None = None,
        time_constraint: str | None = None,
    ) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    special_needs: str = ""
    tasks: list[Task] = field(default_factory=list)

    def set_info(
        self, name: str, species: str, age: int, special_needs: str
    ) -> None:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def edit_task(self, title: str, updates: dict) -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def set_info(
        self, name: str, available_minutes: int, preferences: list[str]
    ) -> None:
        pass

    def add_pet(self, pet: Pet) -> None:
        pass


@dataclass
class DailySchedule:
    date: Date
    time_budget: int
    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    reasoning: dict[str, str] = field(default_factory=dict)

    def generate_plan(self, owner: Owner) -> None:
        pass

    def display_plan(self) -> str:
        pass

    def explain_reasoning(self) -> str:
        pass
