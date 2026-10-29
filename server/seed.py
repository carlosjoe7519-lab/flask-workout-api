
from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise


def seed_data():
    with app.app_context():
        # Add exercises only if they do not already exist.
        exercises_data = [
            {
                "name": "Push-ups",
                "category": "Strength",
                "equipment_needed": False,
            },
            {
                "name": "Squats",
                "category": "Strength",
                "equipment_needed": False,
            },
            {
                "name": "Running",
                "category": "Cardio",
                "equipment_needed": True,
            },
        ]

        for item in exercises_data:
            exercise = Exercise.query.filter_by(name=item["name"]).first()

            if exercise is None:
                exercise = Exercise(**item)
                db.session.add(exercise)

        db.session.flush()

        # Add a sample workout only if it does not already exist.
        workout = Workout.query.filter_by(
            date=date(2026, 10, 29),
            notes="Sample workout from seed script",
        ).first()

        if workout is None:
            workout = Workout(
                date=date(2026, 10, 29),
                duration_minutes=30,
                notes="Sample workout from seed script",
            )
            db.session.add(workout)
            db.session.flush()

        # Link Push-ups to the sample workout only if not already linked.
        pushups = Exercise.query.filter_by(name="Push-ups").first()

        existing_link = WorkoutExercise.query.filter_by(
            workout_id=workout.id,
            exercise_id=pushups.id,
        ).first()

        if existing_link is None:
            db.session.add(
                WorkoutExercise(
                    workout_id=workout.id,
                    exercise_id=pushups.id,
                    reps=10,
                    sets=3,
                )
            )

        db.session.commit()
        print("Seed data added successfully without duplicating existing records.")


if __name__ == "__main__":
    seed_data()
