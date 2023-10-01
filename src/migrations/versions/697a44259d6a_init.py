"""init

Revision ID: 697a44259d6a
Revises: 
Create Date: 2023-08-23 16:17:52.524101

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "697a44259d6a"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("password", sa.Text(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("STAFF", "ADMIN", "SUPER_ADMIN", name="userrolesenum"),
            server_default="STAFF",
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("uuid", name=op.f("users_pkey")),
        sa.UniqueConstraint("email", name=op.f("users_email_key")),
        sa.UniqueConstraint("username", name=op.f("users_username_key")),
        sa.UniqueConstraint("uuid", name=op.f("users_uuid_key")),
    )

    op.create_table(
        "jwt_sessions",
        sa.Column("user_uuid", sa.UUID(), nullable=False),
        sa.Column("refresh_token", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_denied", sa.Boolean(), nullable=False),
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_uuid"], ["users.uuid"], name=op.f("jwt_sessions_user_uuid_fkey"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("uuid", name=op.f("jwt_sessions_pkey")),
        sa.UniqueConstraint("refresh_token", name=op.f("jwt_sessions_refresh_token_key")),
        sa.UniqueConstraint("uuid", name=op.f("jwt_sessions_uuid_key")),
    )

    op.create_index(op.f("jwt_sessions_user_uuid_idx"), "jwt_sessions", ["user_uuid"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("jwt_sessions_user_uuid_idx"), table_name="jwt_sessions")
    op.drop_table("jwt_sessions")
    op.drop_table("users")

    op.execute("DROP TYPE userrolesenum;")
