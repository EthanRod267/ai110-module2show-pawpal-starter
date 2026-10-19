from datetime import date, time

from pawpal_system import DailySchedule, Owner, Pet, Priority, Task, TimeWindow


def main() -> None:
    owner = Owner("Jordan", available_minutes=120, preferences=["morning walks"])

    mochi = Pet("Mochi", "dog", age=3)
    luna = Pet("Luna", "cat", age=5, special_needs="daily thyroid meds")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(
        Task("Morning walk", 30, Priority.HIGH,
             time_window=TimeWindow(time(7, 0), time(8, 30)))
    )
    mochi.add_task(
        Task("Breakfast", 10, Priority.HIGH,
             time_window=TimeWindow(time(7, 30), time(9, 0)))
    )
    mochi.add_task(
        Task("Fetch in the yard", 20, Priority.LOW,
             time_window=TimeWindow(time(16, 0), time(18, 0)))
    )
    luna.add_task(
        Task("Thyroid meds", 5, Priority.HIGH,
             time_window=TimeWindow(time(8, 0), time(8, 30)))
    )
    luna.add_task(
        Task("Brushing", 15, Priority.MEDIUM, frequency="weekly",
             time_window=TimeWindow(time(12, 0)))
    )
    luna.add_task(
        Task("Litter box cleaning", 10, Priority.MEDIUM,
             time_window=TimeWindow(time(18, 0), time(20, 0)))
    )

    schedule = DailySchedule(date.today(), owner)
    schedule.generate_plan(day_start=time(7, 0))

    print("=" * 50)
    print("Today's Schedule")
    print("=" * 50)
    print(schedule.display_plan())
    print()
    print(schedule.explain_reasoning())


if __name__ == "__main__":
    main()
