"""add_document_semantic_metadata_columns (no-op)

Revision ID: 0609a700e797
Revises: 28110bd5385c
Create Date: 2026-07-22 07:22:49.414715

This migration originally added summary, primary_equipment, and revision
columns to the documents table. Those three columns have since been folded
into the initial schema migration (28110bd5385c) so that a fresh database
gets a complete table definition in one shot. This file is retained as a
no-op to keep the Alembic revision chain intact for existing environments
that already ran the original version.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0609a700e797'
down_revision = '28110bd5385c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
