"""Initial migration

Revision ID: 0ed676635924
Revises: 
Create Date: 2025-04-27 00:37:15.773573

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ed676635924'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from app.models.enums import GameStatus, WinnerType, GameRole, QuestionStatus, BotState


def upgrade():
    op.create_table(
        'chats',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('bot_state', sa.Enum(BotState, name='botstate'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('count_wins', sa.Integer(), nullable=True),
        sa.Column('count_losses', sa.Integer(), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'questions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('question_text', sa.Text(), nullable=True),
        sa.Column('answer_text', sa.Text(), nullable=True),
        sa.Column('img_url', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'games',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('chat_id', sa.BigInteger(), nullable=True),
        sa.Column('score_gamers', sa.Integer(), nullable=True),
        sa.Column('score_bot', sa.Integer(), nullable=True),
        sa.Column('round', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum(GameStatus, name='gamestatus'), nullable=True),
        sa.Column('winner', sa.Enum(WinnerType, name='winnertype'), nullable=True),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'games_users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('game_role', sa.Enum(GameRole, name='gamerole'), nullable=True),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'games_questions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=True),
        sa.Column('question_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum(QuestionStatus, name='questionstatus'), nullable=True),
        sa.Column('answering_player', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.ForeignKeyConstraint(['answering_player'], ['games_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('games_questions')
    op.drop_table('games_users')
    op.drop_table('questions')
    op.drop_table('games')
    op.drop_table('users')
    op.drop_table('chats')
    
    # Удаляем enum типы
    sa.Enum(name='botstate').drop(op.get_bind(), checkfirst=False)
    sa.Enum(name='gamestatus').drop(op.get_bind(), checkfirst=False)
    sa.Enum(name='winnertype').drop(op.get_bind(), checkfirst=False)
    sa.Enum(name='gamerole').drop(op.get_bind(), checkfirst=False)
    sa.Enum(name='questionstatus').drop(op.get_bind(), checkfirst=False)