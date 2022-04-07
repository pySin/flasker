"""added a username field

Revision ID: fcf614c7ec17
Revises: f67bb12eb396
Create Date: 2022-03-22 13:59:04.734331

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fcf614c7ec17'
down_revision = 'f67bb12eb396'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('username', sa.String(length=20), nullable=False))
    op.create_unique_constraint(None, 'users', ['username'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'username')
    # ### end Alembic commands ###