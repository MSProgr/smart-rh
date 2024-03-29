"""empty message

Revision ID: 5a849b6431a4
Revises: 0e36c0ac63e6
Create Date: 2020-01-20 11:10:47.798402

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5a849b6431a4'
down_revision = '0e36c0ac63e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('demande', 'structure')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('demande', sa.Column('structure', mysql.VARCHAR(length=120), nullable=False))
    # ### end Alembic commands ###
