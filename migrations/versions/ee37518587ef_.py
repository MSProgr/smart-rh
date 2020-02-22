"""empty message

Revision ID: ee37518587ef
Revises: d41506006835
Create Date: 2020-02-22 15:31:56.591738

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee37518587ef'
down_revision = 'd41506006835'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('facturation_mobile', sa.Column('nbr_puces', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('facturation_mobile', 'nbr_puces')
    # ### end Alembic commands ###