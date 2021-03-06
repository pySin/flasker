"""about author added

Revision ID: 0e180cd2e428
Revises: 6a88df3bb49b
Create Date: 2022-04-07 14:37:06.212988

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e180cd2e428'
down_revision = '6a88df3bb49b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('about_author', sa.Text(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'about_author')
    # ### end Alembic commands ###
