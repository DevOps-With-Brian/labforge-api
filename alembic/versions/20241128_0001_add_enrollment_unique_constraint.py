"""add unique constraint for enrollment course_id and email

Revision ID: 20241128_0001
Revises: 20241125_0001
Create Date: 2024-11-28 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20241128_0001"
down_revision: Union[str, None] = "20241125_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove duplicate enrollments, keeping the earliest one
    op.execute("""
        DELETE FROM enrollments
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM enrollments
            GROUP BY course_id, email
        )
    """)
    op.create_unique_constraint(
        "uq_enrollment_course_email", "enrollments", ["course_id", "email"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_enrollment_course_email", "enrollments", type_="unique")
