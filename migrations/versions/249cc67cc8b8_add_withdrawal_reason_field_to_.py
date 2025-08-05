"""Add withdrawal_reason field to EvaluationRecord

Revision ID: 249cc67cc8b8
Revises: 
Create Date: 2025-07-30 09:58:06.056645

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '249cc67cc8b8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands manually adjusted ###
    op.add_column('evaluation_record', sa.Column('withdrawal_reason', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands manually adjusted ###
    op.drop_column('evaluation_record', 'withdrawal_reason')
    # ### end Alembic commands ###
