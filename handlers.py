from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
import text
import kb
import config
from aiogram import Bot, types
from PIL import Image
import os, shutil
from utils import nn_processor, result_composer
import json

router = Router()

"""
    Запускает функцию ответ на входящее сообщение, если входящее удовлетворяет фильтрам
"""


@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(text.WELLCOME, reply_markup=kb.START_INSTRUCTIONS)


@router.message(F.photo)
async def scanning_results(message: types.Message, bot: Bot):
    photo = message.photo[-1]
    file_id = photo.file_id
    # file = await bot.get_file(file_id)
    disk_file_path = f"{config.DATA_DIR}/{file_id}.jpg"
    # await bot.download(file.file_path, destination=disk_file_path)

    if not os.path.exists(config.DATA_DIR):
        os.mkdir(config.DATA_DIR)

    await bot.download(photo, destination=disk_file_path)

    # Загрузка и обработка изображения
    image = Image.open(disk_file_path)
    # print(type(image))

    # предсказание модели
    prediction = nn_processor.predict(image)

    shutil.rmtree(config.DATA_DIR)

    # Отправка результата пользователю
    await message.answer(text.PHOTO_PROCESSING)
    # await message.reply_photo(message.photo[-1].file_id)
    await bot.send_message(
        text=await result_composer.compose_result(prediction),
        chat_id=message.chat.id,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@router.message(F.text)
async def photo_intructions(message: types.Message):
    if text.PHOTO_REQUIREMENTS_QUESTION in message.text:
        await message.answer(text.PHOTO_REQUIREMENTS)
    elif text.IMPORTANT_QUESTION in message.text:
        await message.answer(text.IMPORTANT)
    elif text.MUSHROOMS_BASE_QUESTION in message.text:
        await message.answer(text.MUSHROOMS_BASE, disable_web_page_preview=True)
    elif text.ABOUT_PROJECT_QUESTION in message.text:
        await message.answer(
            text.ABOUT_PROJECT.format(config.REPOSITORY_LINK),
            disable_web_page_preview=True,
        )
    else:
        await message.answer(text.PHOTO_REQUEST)
