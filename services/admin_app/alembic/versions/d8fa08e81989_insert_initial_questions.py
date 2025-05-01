"""insert_initial_questions

Revision ID: d8fa08e81989
Revises: 0ed676635924
Create Date: 2025-04-27 00:46:28.642969

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8fa08e81989'
down_revision: Union[str, None] = '0ed676635924'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    questions = [
        {"id": 1, "question_text": "Внимание, чёрный ящик. В нём находится то, что обязательно нужно в тумане. Что в чёрном ящике?", "answer_text": "Фары"},
        {"id": 2, "question_text": "Какое изобретение позволяет смотреть сквозь стены?", "answer_text": "Окно"},
        {"id": 3, "question_text": "В одной из стран запрещено давать имена этому животному, так как оно священно. Что это за животное?", "answer_text": "Корова"},
        {"id": 4, "question_text": "Почему американские астронавты не использовали карандаши на орбите?", "answer_text": "Потому что грифель ломкий и опасен в невесомости"},
        {"id": 5, "question_text": "Внимание, чёрный ящик. В нём находится предмет, который помогает находить ответы. Что в нём?", "answer_text": "Книга"},
        {"id": 6, "question_text": "Внимание, чёрный ящик. В нём находится то, что обязательно нужно в тумане. Что в чёрном ящике?", "answer_text": "Фары"},
        {"id": 7, "question_text": "Что может путешествовать по миру, оставаясь в одном и том же углу?", "answer_text": "Почтовая марка"},
        {"id": 8, "question_text": "У какого животного глаза больше, чем его мозг?", "answer_text": "У страуса"},
        {"id": 9, "question_text": "Внимание, чёрный ящик. В нём находится то, что обязательно нужно в тумане. Что в чёрном ящике?", "answer_text": "Фары"},
        {"id": 10, "question_text": "На какой вопрос нельзя ответить \"да\"?", "answer_text": "Вы спите?"},
        {"id": 11, "question_text": "В чёрном ящике находится то, что, по словам японцев, \"рождается дважды: один раз на дереве, другой раз в чашке\". Что в чёрном ящике?", "answer_text": "Чай"},
        {"id": 12, "question_text": "Что можно увидеть с закрытыми глазами?", "answer_text": "Сны"},
        {"id": 13, "question_text": "Что принадлежит вам, но другие используют это чаще, чем вы?", "answer_text": "Ваше имя"},
        {"id": 14, "question_text": "Оно есть у каждого, но нельзя ни потрогать, ни увидеть. При этом его можно потерять. Что это?", "answer_text": "Репутация"},
        {"id": 15, "question_text": "Что всегда перед вами, но вы не можете этого увидеть?", "answer_text": "Будущее"}
    ]

    op.bulk_insert(
        sa.table('questions',
            sa.Column('id', sa.Integer()),
            sa.Column('question_text', sa.Text()),
            sa.Column('answer_text', sa.Text()),
            sa.Column('img_url', sa.String(length=255))
        ),
        questions
    )

def downgrade():
    op.execute("TRUNCATE TABLE questions CASCADE;")
