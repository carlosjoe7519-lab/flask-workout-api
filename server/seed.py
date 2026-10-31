
from datetime import date

from app import app, bcrypt
from models import db, User, Exercise, Workout, WorkoutExercise


def seed_data():
    with app.app_context():

        # Create a demo user if one does not exist.
        user = User.query.filter_by(email="demo@example.com").first()

        if user is None:
            password_hash = bcrypt.generate_password_hash(
                "demo12345"
            ).decode("utf-8")

            user = User(
                username="demo",
                email="demo@example.com",
                password_hash=password_hash,
            )

            db.session.add(user)
            db.session.flush()

        # Add sample exercises.
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
            exercise = Exercise.query.filter_by(
                name=item["name"]
            ).first()

            if exercise is None:
                db.session.add(Exercise(**item))

        db.session.flush()

        # Create a workout for the demo user.
        workout = Workout.query.filter_by(
            user_id=user.id,
            date=date(2026, 10, 29),
            notes="Sample workout from seed script",
        ).first()

        if workout is None:
            workout = Workout(
                user_id=user.id,
                date=date(2026, 10, 29),
                duration_minutes=30,
                notes="Sample workout from seed script",
            )

            db.session.add(workout)
            db.session.flush()

        # Add Push-ups to the sample workout.
        pushups = Exercise.query.filter_by(
            name="Push-ups"
        ).first()

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

        print("Seed data added successfully!")


if __name__ == "__main__":
    seed_data()
