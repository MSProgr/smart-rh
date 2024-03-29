"""empty message

Revision ID: b44a7620c64d
Revises: 
Create Date: 2020-01-18 16:07:58.952978

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b44a7620c64d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('offre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nom', sa.String(length=120), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('nom')
    )
    op.create_table('parc',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nom_parc', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('nom_parc')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('matricule', sa.Integer(), nullable=False),
    sa.Column('nom', sa.String(length=50), nullable=False),
    sa.Column('prenom', sa.String(length=120), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('code_structure', sa.String(length=50), nullable=False),
    sa.Column('groupe', sa.String(length=30), nullable=False),
    sa.Column('identifiant', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=60), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('identifiant'),
    sa.UniqueConstraint('matricule')
    )
    op.create_table('demande',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('motif', sa.Text(), nullable=False),
    sa.Column('nom_projet', sa.String(length=120), nullable=False),
    sa.Column('puces', sa.Integer(), nullable=False),
    sa.Column('pilote', sa.String(length=120), nullable=False),
    sa.Column('structure', sa.String(length=120), nullable=False),
    sa.Column('caracteristiques', sa.Text(), nullable=False),
    sa.Column('etat_demande', sa.Integer(), nullable=False),
    sa.Column('date_demande', sa.DateTime(), nullable=False),
    sa.Column('date_debut', sa.DateTime(), nullable=True),
    sa.Column('date_fin', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('parc_id', sa.Integer(), nullable=False),
    sa.Column('offre_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['offre_id'], ['offre.id'], ),
    sa.ForeignKeyConstraint(['parc_id'], ['parc.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('demande')
    op.drop_table('user')
    op.drop_table('parc')
    op.drop_table('offre')
    # ### end Alembic commands ###
