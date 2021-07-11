"""empty message

Revision ID: 466961e4d03a
Revises: 201b54f0bdb4
Create Date: 2021-07-09 20:26:56.742427

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '466961e4d03a'
down_revision = '201b54f0bdb4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('answers', 'created')
    #op.add_column('answers', sa.Column('created', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('answers', sa.Column('created', postgresql.TIMESTAMP(timezone=True),
                                                  nullable=False))

    op.alter_column('answers', 'created', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('answers', 'created')
    op.add_column('answers', sa.Column('created', sa.Date(), nullable=False))
    # ### end Alembic commands ###
