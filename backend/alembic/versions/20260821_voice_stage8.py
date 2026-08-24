"""voice stage 8 persistence"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260821_voice_stage8"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("voice_conversations",
        sa.Column("id", sa.String(80), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False, index=True),
        sa.Column("title", sa.String(200), nullable=False, server_default="محادثة جديدة"),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)))
    op.create_table("voice_conversation_messages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("conversation_id", sa.String(80), sa.ForeignKey("voice_conversations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tool_name", sa.String(120)),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True)))
    op.create_table("voice_realtime_sessions",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False, index=True),
        sa.Column("conversation_id", sa.String(80), nullable=False, index=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("provider_session_id", sa.String(200)),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("closed_at", sa.DateTime(timezone=True)))
    op.create_table("voice_audit_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False, index=True),
        sa.Column("conversation_id", sa.String(80), index=True),
        sa.Column("event_type", sa.String(80), nullable=False, index=True),
        sa.Column("tool_name", sa.String(120)),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True)))

def downgrade():
    for name in ["voice_audit_events","voice_realtime_sessions","voice_conversation_messages","voice_conversations"]:
        op.drop_table(name)
