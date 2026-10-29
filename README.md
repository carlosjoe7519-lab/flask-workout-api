# Workout API

A Flask REST API for managing workouts and exercises.

**Features:** CRUD operations, exercise-workout relationships, validation, and database migrations.

**Tech:** Python, Flask, SQLAlchemy, Marshmallow, SQLite.

**Run:**
```bash
pipenv install
pipenv run flask --app server/app.py db upgrade
pipenv run python server/seed.py
pipenv run flask --app server/app.py run --port 5555
```