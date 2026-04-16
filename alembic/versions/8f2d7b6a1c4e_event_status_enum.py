"""convert event status to enum

Revision ID: 8f2d7b6a1c4e
Revises: d1ff3e1f469a
Create Date: 2026-04-16 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8f2d7b6a1c4e"
down_revision: Union[str, Sequence[str], None] = "d1ff3e1f469a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


event_status_enum = sa.Enum(
    "draft",
    "published",
    "finished",
    "cancelled",
    name="event_status",
)


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "UPDATE events "
        "SET status = 'draft' "
        "WHERE status NOT IN ('draft', 'published', 'finished', 'cancelled')"
    )

    bind = op.get_bind()
    event_status_enum.create(bind, checkfirst=True)
    op.alter_column(
        "events",
        "status",
        existing_type=sa.String(length=64),
        type_=event_status_enum,
        existing_nullable=False,
        nullable=False,
        postgresql_using="status::event_status",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "events",
        "status",
        existing_type=event_status_enum,
        type_=sa.String(length=64),
        existing_nullable=False,
        nullable=False,
        postgresql_using="status::text",
    )
    event_status_enum.drop(op.get_bind(), checkfirst=True)
