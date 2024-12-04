"""empty message

Revision ID: bea98e782b4c
Revises: 1a4e0bc76f16
Create Date: 2024-11-27 17:59:00.404410

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bea98e782b4c'
down_revision = '1a4e0bc76f16'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('following',
    sa.Column('follower_id', sa.Integer(), nullable=False),
    sa.Column('following_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['following_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('follower_id', 'following_id')
    )
    op.drop_table('follower')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('follower',
    sa.Column('follower_id', sa.INTEGER(), nullable=False),
    sa.Column('following_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['following_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('follower_id', 'following_id')
    )
    op.drop_table('following')
    # ### end Alembic commands ###