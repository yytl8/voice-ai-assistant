"""voice stage 9 agent production controls"""
from alembic import op
import sqlalchemy as sa

revision = "20260821_voice_stage9"
down_revision = "20260821_voice_stage8"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("voice_conversations", sa.Column("workshop_id", sa.Integer(), nullable=True))
    op.create_index("ix_voice_conversations_workshop_id", "voice_conversations", ["workshop_id"])
    op.create_table(
        "voice_attachments",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False, index=True),
        sa.Column("conversation_id", sa.String(80), nullable=False, index=True),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("object_key", sa.String(500), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

def downgrade():
    op.drop_table("voice_attachments")
    op.drop_index("ix_voice_conversations_workshop_id", table_name="voice_conversations")
    op.drop_column("voice_conversations", "workshop_id")
