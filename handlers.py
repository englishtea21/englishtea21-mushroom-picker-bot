from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
import text
import kb
import config
from aiogram import Bot, types
from PIL import Image
import tempfile
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
    
    tmp_photo_file = tempfile.TemporaryFile()

    await bot.download(photo, destination=tmp_photo_file)

    # img donwloading
    image = Image.open(tmp_photo_file)

    # model predictions
    prediction = nn_processor.predict(image)

    # img "in process message"
    await message.answer(text.PHOTO_PROCESSING)
    
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
