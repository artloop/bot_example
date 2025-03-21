from aiogram.types import Message
from sqlalchemy import BigInteger, Integer, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True


# тут мы описываем одун из таблиц нашей базы данных, пусть это будет таблица пользователей бота
class BotUsers(Base):
    __tablename__ = 'bot_users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)



class DataBaseUtils:
    session: async_sessionmaker
    def __init__(self, session_maker: async_sessionmaker):
        self.session = session_maker

    async def add_user(self, message: Message):
        # получаем сессию из пула
        async with self.session() as session:
            # добавление записи в таблицу
            session.add(
                BotUsers(
                    user_id=message.from_user.id,
                )
            )
            try:
                await session.commit()
            except SQLAlchemyError:
                pass

    # Этим методом проверяем, что пользователь есть у нас в базе
    async def check_user(self, message: Message) -> BotUsers:
        async with self.session() as session:
            stmt = select(BotUsers).where(BotUsers.user_id == message.from_user.id)
            raw_result = await session.execute(stmt)
            return raw_result.scalar_one_or_none()
