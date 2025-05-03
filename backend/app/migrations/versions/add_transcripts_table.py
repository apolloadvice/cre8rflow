"""add transcripts table

Revision ID: add_transcripts_table
Revises: 
Create Date: 2024-05-02 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT

# revision identifiers, used by Alembic.
revision = 'add_transcripts_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'transcript',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('video_id', sa.UUID(), nullable=False),
        sa.Column('sentence', sa.String(), nullable=False),
        sa.Column('start', sa.Float(), nullable=False),
        sa.Column('end', sa.Float(), nullable=False),
        sa.Column('embedding', ARRAY(FLOAT), nullable=False),
        sa.ForeignKeyConstraint(['video_id'], ['video.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transcript_video_id'), 'transcript', ['video_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_transcript_video_id'), table_name='transcript')
    op.drop_table('transcript') 