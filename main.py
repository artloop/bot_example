# импорт модуля логирования
import logging
# импорт необходимых модулей из аиограма
from aiogram import Bot, Dispatcher, executor, types
# мопрт фильтров чатов
from aiogram.dispatcher.filters import IDFilter


API_TOKEN = 'вставь сюда токен бота от отца'

# логирование
logging.basicConfig(level=logging.INFO)

# создание бота и диспатчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


# полное совпадение сообщения с этими строками
@dp.message_handler(text=['текст1', 'текст2'])
async def text_in_handler(message: types.Message):
    await message.answer("Это текст")


# текст содержит эти строки
@dp.message_handler(text_contains='example1')
@dp.message_handler(text_contains='example2')
async def text_contains_any_handler(message: types.Message):
    await message.answer("В тексте есть эти строки")


# текст содержит эти оба слова
@dp.message_handler(text_contains=['хуй1', 'хуй2'])
async def text_contains_all_handler(message: types.Message):
    await message.answer("Текст содержит эти слова")


# текст сообщения начинается с этих слов
@dp.message_handler(text_startswith=['пизда1', 'пизда2'])
async def text_startswith_handler(message: types.Message):
    await message.answer("Текст начинается с пизда")


# текст заканчивается на слова
@dp.message_handler(text_endswith=['говно1', 'говно2'])
async def text_endswith_handler(message: types.Message):
    await message.answer("Текст заканчивается на говно")


# этот хэндлер срабатывает на любой текст, если не подошли предыдущие
@dp.message_handler(content_types="text")
async def other_text(message: types.Message):
    # просто выведем что сообще содержится в переменной мессадж в логах, для понимания что она содержит и что мы
    # сможем с ней делать к примеру можем узнать от кого это сообщение пришло его айди будет
    # в message.from_user.id и так можно работать с любыми данными
    logging.warning(message)
    await message.answer("Любой другой текст")


# этот хэндлер будет срабатывать на любые картинки, а удалив в types.ContentType.PHOTO - PHOTO
# можно увидеть какие еще варианты возможны для различных типов данных в телеграмме, но применимы не для всех типов
# чатов для примера types.ContentType.AUDIO будет реагировать на аудио сообщения
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def other_text(message: types.Message):
    await message.answer("Я увидел картинку!")


# также можно встраивать назличные фильтры внутри хэндлера, для более точного определения на что реагировать
# (по-умолчанию бот реагирует на личные сообщения и когда его тэгают в чате),
# при применении IDFilter можно указывать на каких конкретно пользователей он будет реагировать, варианты
# с user_id (для личек пользователей) или chat_id (для конкретных чатов)
@dp.message_handler(IDFilter(user_id=1234), content_types=types.ContentType.VOICE)
async def other_text(message: types.Message):
    await message.answer("Ну нахуй ты рот открыл, один хер корона!")


# это просто запуск аиограмма, если ты явно запускаешь этот файл
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
