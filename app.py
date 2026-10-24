import sys
from datetime import date, time
from pathlib import Path

import streamlit as st

# pawpal_system.py lives in diagrams/, so make it importable from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent / "diagrams"))

from pawpal_system import DailySchedule, Owner, Pet, Priority, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Keep one Owner across reruns; all pets and tasks hang off it.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=120)
owner = st.session_state.owner

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes = int(
        st.number_input(
            "Available minutes today",
            min_value=1,
            max_value=1440,
            value=owner.available_minutes,
        )
    )

st.subheader("Pets")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if any(p.name == pet_name for p in owner.pets):
        st.error(f"{owner.name} already has a pet named {pet_name}.")
    else:
        owner.add_pet(Pet(pet_name, species))

if owner.pets:
    st.table([{"name": p.name, "species": p.species, "tasks": len(p.tasks)} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Each task belongs to one of the owner's pets and feeds into the scheduler.")

if owner.pets:
    pet_for_task = st.selectbox("Pet", [p.name for p in owner.pets])

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        pet = next(p for p in owner.pets if p.name == pet_for_task)
        pet.add_task(Task(task_title, int(duration), Priority[priority.upper()]))

tasks = owner.get_all_tasks()
if tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": t.pet.name if t.pet else "",
                "title": t.title,
                "duration_minutes": t.duration_minutes,
                "priority": t.priority.name.lower(),
            }
            for t in tasks
        ]
    )
else:
    st.info("No tasks yet. Add a pet, then add tasks for it.")

st.divider()

st.subheader("Build Schedule")
day_start = st.time_input("Day starts at", value=time(7, 0))

if st.button("Generate schedule"):
    schedule = DailySchedule(date.today(), owner)
    schedule.generate_plan(day_start=day_start)
    st.code(schedule.display_plan(), language=None)
    st.code(schedule.explain_reasoning(), language=None)
