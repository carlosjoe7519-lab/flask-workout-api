
import os

from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required
)
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, User, Exercise, Workout, WorkoutExercise
from schemas import ExerciseSchema, WorkoutSchema, WorkoutExerciseSchema


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///workout.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY",
    "development-secret-change-before-deployment"
)

db.init_app(app)
migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

workout_exercise_schema = WorkoutExerciseSchema()


# General error handling

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found."}), 404


@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({"errors": error.messages}), 400


@app.errorhandler(IntegrityError)
def handle_integrity_error(error):
    db.session.rollback()

    return jsonify({
        "error": "This record already exists or violates a database rule."
    }), 400


@app.errorhandler(ValueError)
def handle_value_error(error):
    db.session.rollback()
    return jsonify({"error": str(error)}), 400


# Home route

@app.get("/")
def home():
    return jsonify({"message": "Workout API is running."}), 200


# User registration

@app.post("/register")
def register():
    data = request.get_json() or {}

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({
            "error": "Username, email and password are required."
        }), 400

    if not isinstance(username, str) or not isinstance(email, str):
        return jsonify({"error": "Username and email must be text."}), 400

    if not isinstance(password, str):
        return jsonify({"error": "Password must be text."}), 400

    username = username.strip()
    email = email.strip().lower()

    if not username or not email:
        return jsonify({"error": "Username and email cannot be blank."}), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must contain at least 8 characters."
        }), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"error": "Email is already registered."}), 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        username=username,
        email=email,
        password_hash=password_hash
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Account created successfully.",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 201


# User login

@app.post("/login")
def login():
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required."
        }), 400

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"error": "Invalid email or password."}), 400

    user = User.query.filter_by(email=email.strip().lower()).first()

    if user is None:
        return jsonify({"error": "Invalid email or password."}), 401

    password_is_correct = bcrypt.check_password_hash(
        user.password_hash,
        password
    )

    if not password_is_correct:
        return jsonify({"error": "Invalid email or password."}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful.",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 200


# View the logged-in user's details

@app.get("/me")
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if user is None:
        return jsonify({"error": "User not found."}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    }), 200


# Workout routes

@app.get("/workouts")
@jwt_required()
def get_workouts():
    user_id = int(get_jwt_identity())

    page = request.args.get("page", 1, type=int) or 1
    per_page = request.args.get("per_page", 10, type=int) or 10

    if page < 1 or per_page < 1:
        return jsonify({"error": "Page values must be positive."}), 400

    per_page = min(per_page, 100)

    result = Workout.query.filter_by(user_id=user_id).order_by(
        Workout.id
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        "workouts": workouts_schema.dump(result.items),
        "page": result.page,
        "per_page": result.per_page,
        "total": result.total,
        "pages": result.pages
    }), 200


@app.get("/workouts/<int:workout_id>")
@jwt_required()
def get_workout(workout_id):
    user_id = int(get_jwt_identity())

    workout = Workout.query.filter_by(
        id=workout_id,
        user_id=user_id
    ).first()

    if workout is None:
        return jsonify({"error": "Workout not found."}), 404

    return jsonify(workout_schema.dump(workout)), 200


@app.post("/workouts")
@jwt_required()
def create_workout():
    user_id = int(get_jwt_identity())

    data = workout_schema.load(request.get_json() or {})

    workout = Workout(
        date=data["date"],
        duration_minutes=data["duration_minutes"],
        notes=data.get("notes"),
        user_id=user_id
    )

    db.session.add(workout)
    db.session.commit()

    return jsonify(workout_schema.dump(workout)), 201


@app.patch("/workouts/<int:workout_id>")
@jwt_required()
def update_workout(workout_id):
    user_id = int(get_jwt_identity())

    workout = Workout.query.filter_by(
        id=workout_id,
        user_id=user_id
    ).first()

    if workout is None:
        return jsonify({"error": "Workout not found."}), 404

    data = workout_schema.load(
        request.get_json() or {},
        partial=True
    )

    if "date" in data:
        workout.date = data["date"]

    if "duration_minutes" in data:
        workout.duration_minutes = data["duration_minutes"]

    if "notes" in data:
        workout.notes = data["notes"]

    db.session.commit()

    return jsonify(workout_schema.dump(workout)), 200


@app.delete("/workouts/<int:workout_id>")
@jwt_required()
def delete_workout(workout_id):
    user_id = int(get_jwt_identity())

    workout = Workout.query.filter_by(
        id=workout_id,
        user_id=user_id
    ).first()

    if workout is None:
        return jsonify({"error": "Workout not found."}), 404

    db.session.delete(workout)
    db.session.commit()

    return "", 204


# Exercise routes

@app.get("/exercises")
@jwt_required()
def get_exercises():
    exercises = Exercise.query.order_by(Exercise.id).all()

    return jsonify(exercises_schema.dump(exercises)), 200


@app.get("/exercises/<int:exercise_id>")
@jwt_required()
def get_exercise(exercise_id):
    user_id = int(get_jwt_identity())

    exercise = db.session.get(Exercise, exercise_id)

    if exercise is None:
        return jsonify({"error": "Exercise not found."}), 404

    result = exercise_schema.dump(exercise)

    result["workouts"] = [
        workout_schema.dump(link.workout)
        for link in exercise.workout_exercises
        if link.workout.user_id == user_id
    ]

    return jsonify(result), 200


@app.post("/exercises")
@jwt_required()
def create_exercise():
    data = exercise_schema.load(request.get_json() or {})

    exercise = Exercise(
        name=data["name"],
        category=data["category"],
        equipment_needed=data["equipment_needed"]
    )

    db.session.add(exercise)
    db.session.commit()

    return jsonify(exercise_schema.dump(exercise)), 201


@app.delete("/exercises/<int:exercise_id>")
@jwt_required()
def delete_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)

    if exercise is None:
        return jsonify({"error": "Exercise not found."}), 404

    db.session.delete(exercise)
    db.session.commit()

    return "", 204


# Add an exercise to a workout

@app.post(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises"
)
@jwt_required()
def add_exercise_to_workout(workout_id, exercise_id):
    user_id = int(get_jwt_identity())

    workout = Workout.query.filter_by(
        id=workout_id,
        user_id=user_id
    ).first()

    exercise = db.session.get(Exercise, exercise_id)

    if workout is None or exercise is None:
        return jsonify({
            "error": "Workout or exercise not found."
        }), 404

    data = workout_exercise_schema.load(request.get_json() or {})

    link = WorkoutExercise(
        workout_id=workout_id,
        exercise_id=exercise_id,
        reps=data.get("reps"),
        sets=data.get("sets"),
        duration_seconds=data.get("duration_seconds")
    )

    db.session.add(link)
    db.session.commit()

    return jsonify(workout_exercise_schema.dump(link)), 201


if __name__ == "__main__":
    app.run(debug=True, port=5555)
