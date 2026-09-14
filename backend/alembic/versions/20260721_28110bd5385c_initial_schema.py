"""Backfilled initial schema migration.

Revision ID: 28110bd5385c
Revises: 
Create Date: 2026-07-21 23:11:55.149337

This file was originally an empty no-op stub because the schema was created
manually outside of Alembic. It has been backfilled to create all 11 tables
so that `alembic upgrade head` works on a fresh database.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '28110bd5385c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), server_default='engineer', nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # 2. equipment
    op.create_table(
        'equipment',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('tag_number', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('equipment_type', sa.String(length=100), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tag_number')
    )

    # 3. documents
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('filename', sa.String(length=512), nullable=False),
        sa.Column('doc_type', sa.String(length=50), nullable=False),
        sa.Column('file_path', sa.String(length=1024), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('upload_status', sa.String(length=50), server_default='pending', nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('uploaded_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('processed_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('primary_equipment', sa.String(length=255), nullable=True),
        sa.Column('revision', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. equipment_connections
    op.create_table(
        'equipment_connections',
        sa.Column('equipment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('equipment.id'), nullable=False),
        sa.Column('connected_equipment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('equipment.id'), nullable=False),
        sa.Column('relation_type', sa.String(length=50), server_default='physical', nullable=False),
        sa.PrimaryKeyConstraint('equipment_id', 'connected_equipment_id')
    )

    # 5. failure_modes
    op.create_table(
        'failure_modes',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('equipment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('equipment.id'), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. maintenance_events
    op.create_table(
        'maintenance_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('equipment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('equipment.id'), nullable=True),
        sa.Column('event_date', sa.Date(), nullable=True),
        sa.Column('action', sa.Text(), nullable=True),
        sa.Column('addressed_failure_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('failure_modes.id'), nullable=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. regulations
    op.create_table(
        'regulations',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=True),
        sa.Column('title', sa.String(length=512), nullable=True),
        sa.Column('equipment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('equipment.id'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # 8. chunks
    op.create_table(
        'chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('bbox', postgresql.JSONB(), nullable=True),
        sa.Column('section_title', sa.String(length=512), nullable=True),
        sa.Column('equipment_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('embedding_id', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_chunks_document', 'chunks', ['document_id'], unique=False)
    op.create_index('idx_chunks_equipment', 'chunks', ['equipment_ids'], unique=False, postgresql_using='gin')

    # 9. entities
    op.create_table(
        'entities',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('chunk_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chunks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=True),
        sa.Column('entity_text', sa.String(length=512), nullable=True),
        sa.Column('normalized_value', sa.String(length=512), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 10. conversations
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 11. messages
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('citations', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('entities')
    op.drop_index('idx_chunks_equipment', table_name='chunks')
    op.drop_index('idx_chunks_document', table_name='chunks')
    op.drop_table('chunks')
    op.drop_table('regulations')
    op.drop_table('maintenance_events')
    op.drop_table('failure_modes')
    op.drop_table('equipment_connections')
    op.drop_table('documents')
    op.drop_table('equipment')
    op.drop_table('users')
