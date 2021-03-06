"""About Author

Revision ID: 44cfd9c1dec7
Revises: 33eacb8a73aa
Create Date: 2022-02-17 20:21:27.753408

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '44cfd9c1dec7'
down_revision = '33eacb8a73aa'
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
