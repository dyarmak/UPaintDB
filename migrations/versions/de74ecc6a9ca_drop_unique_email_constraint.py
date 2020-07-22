"""drop unique email constraint

Revision ID: de74ecc6a9ca
Revises: 35dbefcf3d1c
Create Date: 2020-07-22 14:47:54.702197

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de74ecc6a9ca'
down_revision = '35dbefcf3d1c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('client_contactEmail_key', 'client', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('client_contactEmail_key', 'client', ['contactEmail'])
    # ### end Alembic commands ###
