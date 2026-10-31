"""Add users and workout ownership"""

from alembic import op
import sqlalchemy as sa


revision = "67bbb38153d3"
down_revision = "c84de5926360"
branch_labels = None
depends_on = None


def upgrade():
    # Create the users table.
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(80), nullable=False),
        sa.Column("email", sa.String(120), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.CheckConstraint(
            "length(trim(username)) > 0",
            name="username_not_blank"
        ),
        sa.CheckConstraint(
            "length(trim(email)) > 0",
            name="email_not_blank"
        ),
        sa.UniqueConstraint("email")
    )

    # Add the user relationship to existing workouts.
    with op.batch_alter_table("workouts", recreate="always") as batch:
        batch.add_column(
            sa.Column("user_id", sa.Integer(), nullable=True)
        )

        batch.create_foreign_key(
            "fk_workouts_user_id_users",
            "users",
            ["user_id"],
            ["id"]
        )


def downgrade():
    # Remove the user relationship from workouts.
    with op.batch_alter_table("workouts", recreate="always") as batch:
        batch.drop_constraint(
            "fk_workouts_user_id_users",
            type_="foreignkey"
        )
        batch.drop_column("user_id")

    # Remove the users table.
    op.drop_table("users")
