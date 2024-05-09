"""oauth_user

Revision ID: 0b2b4c10cfd5
Revises: f63272648786
Create Date: 2024-05-07 22:30:45.292905

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b2b4c10cfd5'
down_revision: Union[str, None] = 'f63272648786'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('oauth_user',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('provider', sa.String(length=10), nullable=False),
    sa.Column('provider_user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_unique_constraint(None, 'device', ['id'])
    op.create_unique_constraint(None, 'refresh_token', ['id'])
    op.create_unique_constraint(None, 'role', ['id'])
    op.create_unique_constraint(None, 'user', ['id'])
    op.create_unique_constraint(None, 'user_history', ['id'])
    op.create_unique_constraint(None, 'user_role', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_role', type_='unique')
    op.drop_constraint(None, 'user_history', type_='unique')
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_constraint(None, 'role', type_='unique')
    op.drop_constraint(None, 'refresh_token', type_='unique')
    op.drop_constraint(None, 'device', type_='unique')
    op.drop_table('oauth_user')
    # ### end Alembic commands ###