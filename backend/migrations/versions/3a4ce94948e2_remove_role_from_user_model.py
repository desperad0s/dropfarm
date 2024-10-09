"""Remove role from User model

Revision ID: 3a4ce94948e2
Revises: fd1a5d7b0d66
Create Date: 2024-10-10 01:27:29.667000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3a4ce94948e2'
down_revision = 'fd1a5d7b0d66'
branch_labels = None
depends_on = None


def upgrade():
    # Convert supabase_uid to UUID
    op.execute('ALTER TABLE "user" ALTER COLUMN supabase_uid TYPE UUID USING supabase_uid::uuid')
    
    # We'll skip the role column removal since it doesn't exist


def downgrade():
    # Convert supabase_uid back to VARCHAR
    op.alter_column('user', 'supabase_uid',
               existing_type=postgresql.UUID(),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)
