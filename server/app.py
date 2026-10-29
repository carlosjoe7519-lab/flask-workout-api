
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import ExerciseSchema, WorkoutSchema, WorkoutExerciseSchema

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///workout.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found."}), 404


@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({"errors": error.messages}), 400


@app.get("/")
def home():
    return jsonify({"message": "Workout API is running."})


@app.get("/workouts")
def get_workouts():
    workouts = Workout.query.order_by(Workout.id).all()
    return jsonify(workouts_schema.dump(workouts)), 200


@app.get("/workouts/<int:workout_id>")
def get_workout(workout_id):
    workout = db.session.get(Workout, workout_id)

    if workout is None:
        return jsonify({"error": "Workout not found."}), 404

    return jsonify(workout_schema.dump(workout)), 200


@app.post("/workouts")
def create_workout():
    data = workout_schema.load(request.get_json() or {})

    workout = Workout(
        date=data["date"],
        duration_minutes=data["duration_minutes"],
        notes=data.get("notes"),
    )

    db.session.add(workout)
    db.session.commit()

    return jsonify(workout_schema.dump(workout)), 201


@app.delete("/workouts/<int:workout_id>")
def delete_workout(workout_id):
    workout = db.session.get(Workout, workout_id)

    if workout is None:
        return jsonify({"error": "Workout not found."}), 404

    db.session.delete(workout)
    db.session.commit()

    return "", 204


@app.get("/exercises")
def get_exercises():
    exercises = Exercise.query.order_by(Exercise.id).all()
    return jsonify(exercises_schema.dump(exercises)), 200


@app.get("/exercises/<int:exercise_id>")
def get_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)

    if exercise is None:
        return jsonify({"error": "Exercise not found."}), 404

    result = exercise_schema.dump(exercise)
    result["workouts"] = [
        workout_schema.dump(link.workout)
        for link in exercise.workout_exercises
    ]

    return jsonify(result), 200


@app.post("/exercises")
def create_exercise():
    data = exercise_schema.load(request.get_json() or {})

    exercise = Exercise(
        name=data["name"],
        category=data["category"],
        equipment_needed=data["equipment_needed"],
    )

    db.session.add(exercise)
    db.session.commit()

    return jsonify(exercise_schema.dump(exercise)), 201


@app.delete("/exercises/<int:exercise_id>")
def delete_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)

    if exercise is None:
        return jsonify({"error": "Exercise not found."}), 404

    db.session.delete(exercise)
    db.session.commit()

    return "", 204


@app.post(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises"
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    exercise = db.session.get(Exercise, exercise_id)

    if workout is None or exercise is None:
        return jsonify({"error": "Workout or exercise not found."}), 404

    data = workout_exercise_schema.load(request.get_json() or {})

    link = WorkoutExercise(
        workout_id=workout_id,
        exercise_id=exercise_id,
        reps=data.get("reps"),
        sets=data.get("sets"),
        duration_seconds=data.get("duration_seconds"),
    )

    db.session.add(link)
    db.session.commit()

    return jsonify(workout_exercise_schema.dump(link)), 201


@app.errorhandler(IntegrityError)
def handle_integrity_error(error):
    db.session.rollback()
    return jsonify({
        "error": "Database constraint failed. Check for duplicate exercises "
                 "or invalid values."
    }), 400


@app.errorhandler(ValueError)
def handle_value_error(error):
    db.session.rollback()
    return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5555)
