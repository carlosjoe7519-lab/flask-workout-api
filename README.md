# Workout API

A Flask REST API that allows users to register, log in, and manage their workouts and exercises.

## Features

- User registration and login
- Secure password hashing
- JWT authentication
- Create, view, update, and delete workouts
- Users can only access their own workouts
- Exercise management
- Add exercises to workouts
- Input validation
- Database migrations
- Pagination for workouts

## Technologies

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Bcrypt
- Flask-JWT-Extended
- Marshmallow
- SQLite

## Installation

Clone the repository:

```bash
git clone https://github.com/carlosjoe7519-lab/flask-workout-api.git
cd flask-workout-api
```

Install the dependencies:

```bash
pipenv install
```

## Database Setup

Run the database migrations:

```bash
pipenv run flask --app server/app.py db upgrade
```

Add sample data:

```bash
pipenv run python server/seed.py
```

## Run the Application

```bash
pipenv run flask --app server/app.py run --port 5555
```

The API will run at:

`http://127.0.0.1:5555`

## Authentication

Register a new account:

`POST /register`

Log in:

`POST /login`

The login endpoint returns a JWT access token.

Include the token when accessing protected routes:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Register a user |
| POST | `/login` | Log in |
| GET | `/me` | Get current user |

### Workouts

| Method | Endpoint | Description |
|---|---|---|
| GET | `/workouts` | Get user's workouts |
| GET | `/workouts/<id>` | Get one workout |
| POST | `/workouts` | Create a workout |
| PATCH | `/workouts/<id>` | Update a workout |
| DELETE | `/workouts/<id>` | Delete a workout |

Workout listing supports pagination using `page` and `per_page` query parameters.

Example:

`GET /workouts?page=1&per_page=10`

### Exercises

| Method | Endpoint | Description |
|---|---|---|
| GET | `/exercises` | Get all exercises |
| GET | `/exercises/<id>` | Get one exercise |
| POST | `/exercises` | Create an exercise |
| DELETE | `/exercises/<id>` | Delete an exercise |

### Workout Exercises

| Method | Endpoint | Description |
|---|---|---|
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout |

## Sample Seed Account

The seed script creates a demo account:

- Email: `demo@example.com`
- Password: `demo12345`

Use this account for local testing only.

## Author

Carlos