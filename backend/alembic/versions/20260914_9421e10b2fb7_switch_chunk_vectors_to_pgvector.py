"""switch_chunk_vectors_to_pgvector

Revision ID: 9421e10b2fb7
Revises: 0609a700e797
Create Date: 2026-09-14 23:00:00.000000

Replaces the external ChromaDB vector store with pgvector so embeddings
live directly on the chunks table in Postgres. Drops the now-unused
embedding_id column (it only ever held a Chroma document id) and adds a
1024-dim embedding column (BAAI/bge-large-en-v1.5's output size).
"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '9421e10b2fb7'
down_revision = '0609a700e797'
branch_labels = None
depends_on = None

EMBEDDING_DIM = 1024


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column('chunks', sa.Column('embedding', Vector(EMBEDDING_DIM), nullable=True))
    op.drop_column('chunks', 'embedding_id')


def downgrade() -> None:
    op.add_column('chunks', sa.Column('embedding_id', sa.String(length=255), nullable=True))
    op.drop_column('chunks', 'embedding')
