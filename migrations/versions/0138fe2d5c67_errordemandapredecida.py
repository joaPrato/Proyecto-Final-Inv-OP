"""errorDemandaPredecida

Revision ID: 0138fe2d5c67
Revises: 5f95ba8bfb89
Create Date: 2024-06-28 04:13:26.220064

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0138fe2d5c67'
down_revision = '5f95ba8bfb89'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('error_demanda_predecida', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nombreMetodo', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('error_DP', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('cantidad_periodos', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('numero_raiz', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('alfa', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('error_demanda_predecida', schema=None) as batch_op:
        batch_op.drop_column('alfa')
        batch_op.drop_column('numero_raiz')
        batch_op.drop_column('cantidad_periodos')
        batch_op.drop_column('error_DP')
        batch_op.drop_column('nombreMetodo')

    # ### end Alembic commands ###