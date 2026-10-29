
from marshmallow import Schema, fields, validates, validates_schema, ValidationError
from marshmallow.validate import Length, Range


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=Length(min=1, max=100))
    category = fields.Str(required=True, validate=Length(min=1, max=50))
    equipment_needed = fields.Bool(required=True)

    @validates("name")
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Name cannot be blank.")

    @validates("category")
    def validate_category(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Category cannot be blank.")


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(
        required=False,
        allow_none=True,
        validate=Range(min=1),
    )
    sets = fields.Int(
        required=False,
        allow_none=True,
        validate=Range(min=1),
    )
    duration_seconds = fields.Int(
        required=False,
        allow_none=True,
        validate=Range(min=1),
    )
    exercise = fields.Nested(ExerciseSchema, dump_only=True)

    @validates_schema
    def validate_measurements(self, data, **kwargs):
        measurements = ("reps", "sets", "duration_seconds")
        if not any(data.get(field) is not None for field in measurements):
            raise ValidationError(
                "Provide at least one of reps, sets, or duration_seconds."
            )


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(
        required=True,
        validate=Range(min=1),
    )
    notes = fields.Str(required=False, allow_none=True)
    workout_exercises = fields.Nested(
        WorkoutExerciseSchema,
        many=True,
        dump_only=True,
    )
    exercises = fields.Nested(ExerciseSchema, many=True, dump_only=True)
