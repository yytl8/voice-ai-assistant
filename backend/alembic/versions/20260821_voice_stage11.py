"""voice stage 11 integration support"""
from alembic import op
import sqlalchemy as sa

revision = "20260821_voice_stage11"
down_revision = "20260821_voice_stage9"
branch_labels = None
depends_on = None

def upgrade():
    op.create_index(
        "ix_voice_messages_conversation_created",
        "voice_conversation_messages",
        ["conversation_id", "created_at"],
    )

def downgrade():
    op.drop_index(
        "ix_voice_messages_conversation_created",
        table_name="voice_conversation_messages",
    )
