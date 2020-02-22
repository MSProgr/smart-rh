"""empty message

Revision ID: 3a596735e5f0
Revises: ee37518587ef
Create Date: 2020-02-22 15:37:29.310748

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3a596735e5f0'
down_revision = 'ee37518587ef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('facturation_mobile', sa.Column('total_mois', sa.Integer(), nullable=False))
    op.drop_column('facturation_mobile', 'total')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('facturation_mobile', sa.Column('total', mysql.VARCHAR(length=20), nullable=False))
    op.drop_column('facturation_mobile', 'total_mois')
    # ### end Alembic commands ###