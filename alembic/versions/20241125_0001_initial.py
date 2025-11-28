"""initial schema for courses, enrollments, labs"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20241125_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types first using raw SQL to handle idempotency
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'coursestatus') THEN
                    CREATE TYPE coursestatus AS ENUM ('draft', 'published', 'archived');
                END IF;
            END$$;
            """
        )
    )
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'labresourcetype') THEN
                    CREATE TYPE labresourcetype AS ENUM ('yaml','terraform','kubernetes','docker_compose','walkthrough','link','other');
                END IF;
            END$$;
            """
        )
    )

    # Create tables using raw SQL column types to avoid SQLAlchemy enum auto-creation
    op.create_table(
        "courses",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("title", sa.String(length=140), nullable=False),
        sa.Column("overview", sa.Text(), nullable=True),
        sa.Column("instructor", sa.String(length=80), nullable=False),
        sa.Column("primary_video_url", sa.String(length=500), nullable=False),
        sa.Column("supplemental_urls", sa.JSON(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("difficulty", sa.String(length=20), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("prerequisites", sa.JSON(), nullable=True),
        sa.Column("category", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Cast the status column to use the enum type
    op.execute(sa.text("ALTER TABLE courses ALTER COLUMN status TYPE coursestatus USING status::coursestatus"))

    op.create_table(
        "enrollments",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("course_id", sa.String(length=36), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("progress_percent", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "lab_exercises",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("course_id", sa.String(length=36), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=140), nullable=False),
        sa.Column("summary", sa.String(length=1000), nullable=True),
        sa.Column("resource_type", sa.String(length=50), nullable=False),
        sa.Column("resource_uri", sa.String(length=500), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
    )

    # Cast the resource_type column to use the enum type
    op.execute(sa.text("ALTER TABLE lab_exercises ALTER COLUMN resource_type TYPE labresourcetype USING resource_type::labresourcetype"))


def downgrade() -> None:
    op.drop_table("lab_exercises")
    op.drop_table("enrollments")
    op.drop_table("courses")

    bind = op.get_bind()
    sa.Enum(name="coursestatus").drop(bind, checkfirst=True)
    sa.Enum(name="labresourcetype").drop(bind, checkfirst=True)
