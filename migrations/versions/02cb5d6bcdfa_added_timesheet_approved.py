"""added Timesheet.approved

Revision ID: 02cb5d6bcdfa
Revises: fab33cec10c4
Create Date: 2020-12-03 19:29:32.271971

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02cb5d6bcdfa'
down_revision = 'fab33cec10c4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('timesheet', sa.Column('approved', sa.Boolean(), nullable=True))
    op.execute('UPDATE timesheet SET approved = false')
    op.alter_column('timesheet', 'approved', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('timesheet', 'approved')
    # ### end Alembic commands ###