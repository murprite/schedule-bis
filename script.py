#6149557967:AAGplgzjTwIWFPZLrBFjzFK-MTkAqAQFNfQ

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from bs4 import BeautifulSoup

TOKEN = "6149557967:AAGplgzjTwIWFPZLrBFjzFK-MTkAqAQFNfQ"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def SuperStart(message: types.Message):
    await message.answer("Hello")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
