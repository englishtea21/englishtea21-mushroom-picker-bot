import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
from utils import bot
from handlers import router


async def main():
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    """
    удаляет все обновления, которые произошли после последнего завершения работы бота. 
    Это нужно, чтобы бот обрабатывал только те сообщения, которые пришли ему непосредственно во время его работы, 
    а не за всё время. следующая строка запускает бота.
    """
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
