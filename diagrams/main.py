from datetime import date, time

from pawpal_system import DailySchedule, Owner, Pet, Priority, Task, TimeWindow


def print_tasks(heading: str, tasks: list[Task]) -> None:
    print(heading)
    if not tasks:
        print("  (none)")
    for task in tasks:
        start = task.time_window.earliest if task.time_window else None
        start_str = f"{start:%H:%M}" if start else "--:--"
        check = "x" if task.completed else " "
        print(f"  [{check}] {start_str}  {task.title} ({task.pet.name})")
    print()


def main() -> None:
    owner = Owner("Jordan", available_minutes=120, preferences=["morning walks"])

    mochi = Pet("Mochi", "dog", age=3)
    luna = Pet("Luna", "cat", age=5, special_needs="daily thyroid meds")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Tasks are added deliberately out of time order to exercise sort_by_time().
    mochi.add_task(
        Task("Fetch in the yard", 20, Priority.LOW,
             time_window=TimeWindow(time(16, 0), time(18, 0)))
    )
    luna.add_task(
        Task("Litter box cleaning", 10, Priority.MEDIUM,
             time_window=TimeWindow(time(18, 0), time(20, 0)))
    )
    mochi.add_task(
        Task("Breakfast", 10, Priority.HIGH,
             time_window=TimeWindow(time(7, 30), time(9, 0)))
    )
    luna.add_task(Task("Play with feather toy", 15, Priority.LOW))
    luna.add_task(
        Task("Brushing", 15, Priority.MEDIUM, frequency="weekly",
             time_window=TimeWindow(time(12, 0)))
    )
    meds = Task("Thyroid meds", 5, Priority.HIGH,
                time_window=TimeWindow(time(8, 0), time(8, 30)))
    luna.add_task(meds)
    mochi.add_task(
        Task("Morning walk", 30, Priority.HIGH,
             time_window=TimeWindow(time(7, 0), time(8, 30)))
    )

    # Mark one done so the completion filter has something to show.
    meds.mark_complete()

    schedule = DailySchedule(date.today(), owner)

    print("=" * 50)
    print("Sorting & Filtering")
    print("=" * 50)
    print_tasks("All tasks (as added):", owner.get_all_tasks())
    print_tasks("All tasks sorted by time:", schedule.sort_by_time())
    print_tasks("Completed:", owner.filter_tasks(completed=True))
    print_tasks("Still to do, sorted:", schedule.sort_by_time(owner.filter_tasks(completed=False)))
    print_tasks("Mochi only:", owner.filter_tasks(pet_name="mochi"))
    print_tasks("Luna, still to do:", owner.filter_tasks(completed=False, pet_name="Luna"))
    print_tasks("Unknown pet 'Rex':", owner.filter_tasks(pet_name="Rex"))

    schedule.generate_plan(day_start=time(7, 0))

    print("=" * 50)
    print("Today's Schedule")
    print("=" * 50)
    print(schedule.display_plan())
    print()
    print(schedule.explain_reasoning())


if __name__ == "__main__":
    main()
