# импорт модуля логирования
import asyncio
import logging

# импорт необходимых модулей из аиограма
from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from database import Base, DataBaseUtils
from filters import ChatTypeFilter

API_TOKEN = '7135012880:AAEpZ51oX4sxFtDx0nvZRZVTdRucFEkhTfQ'

# логирование
logging.basicConfig(level=logging.INFO)
logs = logging.getLogger(__name__)

# Роутер Aiogram
router = Router()

# Magic filter docs https://docs.aiogram.dev/en/v3.19.0/dispatcher/filters/magic_filters.html


# реакция на команду /start
@router.message(Command(commands=['start']))
async def start(message: Message, database: DataBaseUtils, privileged_user_ids: set):
    # из переменной, которая используется при старте приложения получаем список пользователей,
    # если текущий есть в этом списке выводим соответствующее сообщение
    if message.from_user.id in privileged_user_ids:
        await message.answer("Вы привелигированный пользователь!")
        return
    # для остальных выводим приветствие, если они пришли к нам впервые
    # делая запрос к базе данных
    user = await database.check_user(message)
    if user:
        await message.answer("О, давно не виделись!")
    else:
        await message.answer("Привет, я вижу тебя впервые!")
        await database.add_user(message)


# полное совпадение сообщения с этими строками
@router.message(F.text.in_(['текст1', 'текст2']))
async def text_in_handler(message: Message):
    await message.answer("Это текст")


# текст содержит эти строки
@router.message(F.text.contains('example1'))
@router.message(F.text.contains('example2'))
async def text_contains_any_handler(message: Message):
    await message.answer("В тексте есть эти строки")


# Пример кастомного фильтра если нужны более сложные условия фильтрации
# Фильтры можно применять как на отдельные хэндлеры, так и на роутер целиком
# например так, при создании роутера
# channel_router = Router()
# channel_router.message.filter(ChatTypeFilter([ChatType.CHANNEL]))
@router.message(ChatTypeFilter([ChatType.CHANNEL]))
async def chat_type_filter(message: Message):
    await message.answer("Сообщение было отправено из канала!")


# этот хэндлер срабатывает на любой текст, если не подошли предыдущие
@router.message(F.text)
async def other_text(message: Message):
    # просто выведем что сообще содержится в переменной мессадж в логах, для понимания что она содержит и что мы
    # сможем с ней делать к примеру можем узнать от кого это сообщение пришло его айди будет
    # в message.from_user.id и так можно работать с любыми данными
    logs.warning(message)
    await message.answer("Любой другой текст")


# этот хэндлер будет срабатывать на любые картинки.
# Можно отфильтровать также любое поле необходимого события, а сами поля можно найти в документации TG
# например на тип сообщений https://core.telegram.org/bots/api#message
@router.message(F.photo)
async def other_text(message: Message):
    await message.answer("Я увидел картинку!")


# Пример двойной фильтрации, когда мы точно знаем от какого ID пользователя придет Аудио сообщение
@router.message(F.from_user.id == 1234, F.audio)
async def other_text(message: Message):
    await message.answer("Это голосовуха!")



async def starter():
    # создание бота и диспатчера
    logs.warning("Start application!")

    # Также можно изжектить какие-либо свои объекты в Dispatcher, чтобы потом их использовать
    privileged_user_ids = {2345, 678}

    # Инициализация базы данных
    engine = create_async_engine("sqlite+aiosqlite:///database.db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    # Объявление бота и диспетчера, прослушивающего события от Telegram
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Подключение наших роутеров, в примере только один и все зависит от необходимостей
    dp.include_router(router)

    try:
        # Старт прослушивания событий из телеграм, он выполняется бесконечно до прерывания
        await dp.start_polling(
            bot,
            privileged_user_ids=privileged_user_ids,
            database=DataBaseUtils(session_maker=session_maker)
        )
    except KeyboardInterrupt:
        pass


# это просто запуск аиограмма, если ты явно запускаешь этот файл
if __name__ == '__main__':
    try:
        asyncio.run(starter())
    except KeyboardInterrupt:
        logs.warning('Application finished!')
