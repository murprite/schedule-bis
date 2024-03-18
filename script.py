# 6149557967:AAGplgzjTwIWFPZLrBFjzFK-MTkAqAQFNfQ

import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, Filter
from bs4 import BeautifulSoup
import requests
import re

TOKEN = "6149557967:AAGplgzjTwIWFPZLrBFjzFK-MTkAqAQFNfQ"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


class MyFilter(Filter):
    def __init__(self, text: str) -> None:
        self.text = text.lower()

    async def __call__(self, message: types.Message) -> bool:
        return self.text == "завтра" or self.text == "сегодня"


class UserData:
    users = []
    
    def __init__(self):
        with open("data.json", "r") as read_data:
            self.users = json.loads(read_data.read())

    def savedata(self):
        try:
            with open("data.json", "w") as write_data:
                json.dump(self.users, write_data)
        except:
            print("Saving of JSON file is failed")
        
        print("Data is saved")


def find_user(user_id: int, data: dict) -> dict | bool:
    for elem in data["users"]:
        if elem["user_id"] == user_id:
            return elem
    return False


dataDispatcher = UserData()
kb = [
        [
            types.KeyboardButton(text="Сегодня"),
            types.KeyboardButton(text="Завтра")
        ],
    ]
keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def start(message: types.Message):
    user = find_user(message.from_user.id, dataDispatcher.users)
    
    if user:
        await message.answer("Привет")
    else:
        await message.answer("Новый пользователь. Укажите подгруппу и ID группы")
        
        new_user = {"user_id": message.from_user.id, "user_name": message.from_user.first_name, "subgroup": None, "group_id": None}
        dataDispatcher.users["users"].append(new_user)
        dataDispatcher.savedata()


@dp.message(Command("set_subgroup"))
async def selectingSubgroup(message: types.Message):
    
    if len(message.text.split()) != 2:
        return await message.answer("Дебил, группа это 1 число. Совсем даун.")
    user = find_user(message.from_user.id, dataDispatcher.users)
    
    user["subgroup"] = message.text.split()[1]
    dataDispatcher.savedata()
    await message.answer("Подгруппа указана", reply_markup=keyboard)


@dp.message(Command("set_group"))
async def selectGroup(message: types.Message):
    if len(message.text.split()) != 2:
        return await message.answer("Дебил, группа это 1 число. Совсем даун.")

    user = find_user(message.from_user.id, dataDispatcher.users)
    user["group_id"] = message.text.split()[1]
    dataDispatcher.savedata()
    await message.answer("Группа указана", reply_markup=keyboard)


@dp.message(MyFilter(F.text))
async def day_handler(message: types.Message):
    user = find_user(message.from_user.id, dataDispatcher.users)

    data = requests.get("https://timetable.pallada.sibsau.ru/timetable/group/" + user["group_id"]).text

    parse = BeautifulSoup(data, features="html.parser")

    week1 = parse.find(id="week_1_tab")
    week2 = parse.find(id="week_2_tab")

    current_week = week1 if week1.find(attrs={"class": "today"}) else week2

    current_day = current_week.find_all(attrs={"class": "today"})[0] if message.text.lower() != "завтра" else (
            current_week.find_all(attrs={"class": "today"})[0].find_next_sibling("div", attrs={"class": "day"})
    )

    if current_day is not None:
        lines = current_day.find_all("div", attrs={"class": "line"})
        text = ''
        for discipline in lines:
            current = discipline.find_all("li")
            time = discipline.find_all("div", {"class": "time"})[0].select_one(".hidden-xs").text.strip()

            if current[0].text == "* подгруппа":
                current.pop(0)
            if len(current) == 4:
                subgroup = int(re.findall(r"\d+", current[3].text)[0])
                if subgroup == int(user["subgroup"]):
                    text += f"Предмет: {current[0].text}\n"
                    text += f"Преподаватель: {current[1].text}\n"
                    text += f"Место: {current[2].text}\n"
                    text += f"Время: {time}\n\n"

                else:
                    continue
            else:
                text += f"Предмет: {current[0].text}\n"
                text += f"Преподаватель: {current[1].text}\n"
                text += f"Место: {current[2].text}\n"
                text += f"Время: {time}\n\n"

        await message.answer(text, reply_markup=keyboard)
    else:
        await message.answer("На завтра ничего нет", reply_markup=keyboard)


@dp.message(Command("get_user"))
async def getCurrentUser(message: types.Message):
    user = find_user(message.from_user.id, dataDispatcher.users)
    text = ''

    text += f"ID группы: {user["group_id"]}\n"
    text += f"Подгруппа: {user["subgroup"]}\n\n"
    text += f"Другие подгруппы: {"Включены" if user["showSubgroups"] else "Выключены"}\n"

    await message.answer(text, reply_markup=keyboard)

@dp.message(Command("show_other"))
async def showOtherSubgroup(message: types.Message):
    user = find_user(message.from_user.id, dataDispatcher.users)

    user["showSubgroups"] = not user["showSubgroups"]
    dataDispatcher.savedata()

    await message.answer("Другие подгруппы выключены" if not user["showSubgroups"] else "Другие подгруппы включены")

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":  
    dataDispatcher.savedata()
    asyncio.run(main())
    