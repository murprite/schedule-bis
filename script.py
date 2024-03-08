# 6149557967:AAGplgzjTwIWFPZLrBFjzFK-MTkAqAQFNfQ

import asyncio
import json
import logging
from typing import Type
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from bs4 import BeautifulSoup
import requests
import re

TOKEN = "6149557967:AAGplgzjTwIWFPZLrBFjzFK-MTkAqAQFNfQ"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


class UserData():
    users = []
    
    def __init__(self):
        with open("data.json", "r") as read_data:
            self.users = json.loads(read_data.read())

    def saveUserData(self):
        try:
            with open("data.json", "w") as write_data:
                json.dump(self.users, write_data)
        except:
            print("Saving of JSON file is failed")
        
        print("Data is saved")


def find_user(user_id: int, data: list) -> dict | bool:
    for elem in data["users"]:
        if elem["user_id"] == user_id:
            return elem
    return False
        

dataDispatcher = UserData()


@dp.message(Command("start"))
async def start(message: types.Message):
    user = find_user(message.from_user.id, dataDispatcher.users)
    
    if user:
        await message.answer("Привет");
    else:
        await message.answer("Новый пользователь. Укажите подгруппу и ID группы (эксперимитально)")
        
        new_user = {"user_id": message.from_user.id, "user_name": message.from_user.first_name, "subgroup": None, "group_id": None}
        dataDispatcher.users["users"].append(new_user)
        dataDispatcher.saveUserData()


@dp.message(Command("set_subgroup"))
async def selectingSubgroup(message: types.Message):
    
    if len(message.text.split()) != 2:
        return await message.answer("Дебил, группа это 1 число. Совсем даун.")
    user = find_user(message.from_user.id, dataDispatcher.users)
    
    user["subgroup"] = message.text.split()[1]
    dataDispatcher.saveUserData()
    await message.answer("Подгруппа указана")


@dp.message(Command("set_group"))
async def selectGroup(message: types.Message):
    if len(message.text.split()) != 2:
        return await message.answer("Дебил, группа это 1 число. Совсем даун.")

    user = find_user(message.from_user.id, dataDispatcher.users)
    user["group_id"] = message.text.split()[1]
    dataDispatcher.saveUserData()
    await message.answer("Группа указана")


@dp.message(Command("today"))
async def today(message: types.Message):
    user = find_user(message.from_user.id, dataDispatcher.users)
    
    data = requests.get("https://timetable.pallada.sibsau.ru/timetable/group/" + user["group_id"]).text
    
    parse = BeautifulSoup(data, features="html.parser")

    week1 = parse.find(id="week_1_tab")
    week2 = parse.find(id="week_2_tab")

    current_week = None
    if week1.find(attrs={"class": "today"}):
        current_week = week1
    else:
        current_week = week2

    current_day = current_week.find(attrs={"class": "today"})
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
                    text += f"Предмет: {current[0].text}. Подгруппа: {subgroup}\n"
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

        await message.answer(text)
    else:
        await message.answer("На сегодня ничего нет")

@dp.message(Command("tomorrow"))
async def tomorrow(message: types.Message):
    user = find_user(message.from_user.id, dataDispatcher.users)

    data = requests.get("https://timetable.pallada.sibsau.ru/timetable/group/" + user["group_id"]).text

    parse = BeautifulSoup(data, features="html.parser")

    week1 = parse.find(id="week_1_tab")
    week2 = parse.find(id="week_2_tab")

    current_week = None
    if week1.find(attrs={"class": "today"}):
        current_week = week1
    else:
        current_week = week2

    current_day = current_week.find(attrs={"class": "today"}).find_next_sibling("div", {"class": "day"})
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

        await message.answer(text)
    else:
        await message.answer("На завтра ничего нет")


@dp.message(Command("get_user"))
async def getCurrentUser(message: types.Message):
    user = find_user(message.from_user.id, dataDispatcher.users)
    
    await message.answer("Иди нахуй, мне лень делать метод")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":  
    dataDispatcher.saveUserData()
    asyncio.run(main())