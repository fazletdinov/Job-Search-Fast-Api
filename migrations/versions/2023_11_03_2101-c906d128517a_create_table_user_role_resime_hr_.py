"""create table user, role, resime, hr, vacansy, comment

Revision ID: c906d128517a
Revises: 
Create Date: 2023-11-03 21:01:32.440695

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c906d128517a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('hr',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('first_name', sa.String(length=250), nullable=False),
    sa.Column('last_name', sa.String(length=250), nullable=False),
    sa.Column('middle_name', sa.String(length=250), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('company_name', sa.String(length=250), nullable=False),
    sa.Column('about_the_company', sa.String(length=3000), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), nullable=True),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('resume',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('first_name', sa.String(length=250), nullable=False),
    sa.Column('last_name', sa.String(length=250), nullable=False),
    sa.Column('middle_name', sa.String(length=250), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('experience', sa.String(length=250), nullable=False),
    sa.Column('education', sa.String(length=250), nullable=False),
    sa.Column('about', sa.String(length=3000), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), nullable=True),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_role',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vacansy',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('place_of_work', sa.String(length=250), nullable=False),
    sa.Column('required_specialt', sa.String(length=500), nullable=False),
    sa.Column('proposed_salary', sa.String(length=120), nullable=False),
    sa.Column('working_conditions', sa.String(length=250), nullable=False),
    sa.Column('required_experience', sa.String(length=250), nullable=False),
    sa.Column('vacant', sa.String(length=20), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), nullable=True),
    sa.Column('hr_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['hr_id'], ['hr.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comment',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('text', sa.String(length=1000), nullable=False),
    sa.Column('created', sa.DateTime(timezone=True), nullable=True),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('vacansy_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['vacansy_id'], ['vacansy.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comment')
    op.drop_table('vacansy')
    op.drop_table('user_role')
    op.drop_table('resume')
    op.drop_table('hr')
    op.drop_table('user')
    op.drop_table('role')
    # ### end Alembic commands ###
