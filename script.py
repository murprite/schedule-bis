#6149557967:AAGplgzjTwIWFPZLrBFjzFK-MTkAqAQFNfQ

import asyncio
import json
import logging
from typing import Type
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from bs4 import BeautifulSoup
import requests

TOKEN = "6149557967:AAGplgzjTwIWFPZLrBFjzFK-MTkAqAQFNfQ"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

class UserData():
    users = []
    
    def __init__(self):
        with open("data.json", "r") as read_data:
            self.users = json.loads(read_data.read())
            print(type(self.users))
    def SaveUserData(self):
        try:
            with open("data.json", "w") as write_data:
                json.dump(self.users, write_data)
        except:
            print("Saving of JSON file is failed")
        
        print("Data is saved")
        
def find_user(user_id: int, data: list):
    for elem in data["users"]:
        if(elem["user_id"] == user_id):
            return elem
    return False
        

dataDispatcher = UserData()
@dp.message(Command("start"))
async def Start(message: types.Message):
    user = find_user(message.from_user.id, dataDispatcher.users)
    
    if user:
        await message.answer("Привет");
    else:
        await message.answer("Новый пользователь. Укажите подгруппу и ID группы (эксперимитально)")
        
        new_user = {"user_id": message.from_user.id, "user_name": message.from_user.first_name, "subgroup": None, "group_id": None}
        dataDispatcher.users["users"].append(new_user)
        dataDispatcher.SaveUserData()

@dp.message(Command("set_subgroup"))
async def SelectingSubgroup(message: types.Message):
    
    if len(message.text.split()) != 2:
        return await message.answer("Дебил, группа это 1 число. Совсем даун.")
    user = find_user(message.from_user.id, dataDispatcher.users)
    
    user["subgroup"] = message.text.split()[1]
    await message.answer("Подгруппа указана")
    dataDispatcher.SaveUserData()

@dp.message(Command("set_group"))
async def SelectGroup(message: types.Message):
    if len(message.text.split()) != 2:
        return await message.answer("Дебил, группа это 1 число. Совсем даун.")
    
    user = find_user(message.from_user.id, dataDispatcher.users)
    user["group_id"] = message.text.split()[1]
    dataDispatcher.SaveUserData()
    await message.answer("Группа указана")
    
async def main():
    await dp.start_polling(bot)

@dp.message(Command("tomorrow"))
async def Tomorrow(message: types.Message):
    user = find_user(message.from_user.id, dataDispatcher.users)
    
    data = requests.get("https://timetable.pallada.sibsau.ru/timetable/group/" + user["group_id"])
    
    parse = BeautifulSoup(data)
    
    

if __name__ == "__main__":  
    dataDispatcher.SaveUserData()
    asyncio.run(main())