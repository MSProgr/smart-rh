"""empty message

Revision ID: dffd124ae568
Revises: dc037325373c
Create Date: 2020-01-30 22:51:14.731026

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dffd124ae568'
down_revision = 'dc037325373c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('agence',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nom', sa.String(length=120), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('nom')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('agence')
    # ### end Alembic commands ###
