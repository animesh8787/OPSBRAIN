"""switch_auth_to_firebase

Revision ID: a7c3f9e1d4b2
Revises: 9421e10b2fb7
Create Date: 2026-09-15 00:00:00.000000

Replaces password-based auth (hashed_password + our own JWTs) with
Firebase Authentication. Users are now identified by their Firebase UID;
the app no longer stores or checks passwords. Existing rows predate
Firebase accounts and can't be mapped to a UID, so they're cleared -
users sign in again through Firebase and get a fresh row on first request.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a7c3f9e1d4b2'
down_revision = '9421e10b2fb7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM users")
    op.add_column('users', sa.Column('firebase_uid', sa.String(length=128), nullable=False))
    op.create_unique_constraint('uq_users_firebase_uid', 'users', ['firebase_uid'])
    op.drop_column('users', 'hashed_password')


def downgrade() -> None:
    op.add_column('users', sa.Column('hashed_password', sa.String(length=255), nullable=True))
    op.drop_constraint('uq_users_firebase_uid', 'users', type_='unique')
    op.drop_column('users', 'firebase_uid')
