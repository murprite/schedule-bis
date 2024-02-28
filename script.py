# 6149557967:AAGplgzjTwIWFPZLrBFjzFK-MTkAqAQFNfQ

import dis
from email import message
import logging
from multiprocessing import context
import re
from datetime import datetime
from sqlite3 import Date
from turtle import up
from unittest.mock import DEFAULT
from xml.dom.minidom import CharacterData
from bs4 import BeautifulSoup
import asyncio
import requests
from telegram import Update, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

token = "6149557967:AAGplgzjTwIWFPZLrBFjzFK-MTkAqAQFNfQ"
button1 = InlineKeyboardButton("Сегодня", callback_data="today")
button2 = InlineKeyboardButton("Завтра", callback_data="tomorrow")
lastMessage = ''

async def Start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    
    
    message = await context.bot.send_message(chat_id=update.effective_chat.id, text="Выбери опцию", reply_markup=markup)

        
async def Today(update: Update, context: ContextTypes.DEFAULT_TYPE):
        
    result = await asyncio.to_thread(requests.get, 'https://timetable.pallada.sibsau.ru/timetable/group/13491')
   
    day = BeautifulSoup(result.text, features="html.parser").find("div", {"class": "today"})
        
    disciplines = day.select(".line")
        
    output = ""
    for line in disciplines:
        time = line.find("div", {"class": "hidden-xs"}).getText().strip()
            
        lis = line.findAll("li")

        splitted_2 = time.split("-")[1].split(":")
        seconds_2 = int(splitted_2[0]) * 3600 + int(splitted_2[1]) * 60

        output += time + "\n"
        for li in lis:
            output += li.getText() + "\n"
        output += "\n"
    await context.bot.editMessageText(chat_id=update.effective_chat.id, text=output, message_id=messageID, reply_markup=markup)

async def Tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if(datetime.weekday(datetime.now()) == 5):
        await context.bot.editMessageText(chat_id=update.effective_chat.id, text="Завтра воскресенье", message_id=messageID, reply_markup=markup)
        return;

    result = await asyncio.to_thread(requests.get, 'https://timetable.pallada.sibsau.ru/timetable/group/13491')
    
    day = BeautifulSoup(result.text, features="html.parser").select(".today + div")[0]
    disciplines = day.select(".line")
        
    output = ""
        
    for line in disciplines:
        time = line.find("div", {"class": "hidden-xs"}).getText().strip()
        
        splitted_2 = time.split("-")[1].split(":")
        seconds_2 = int(splitted_2[0]) * 3600 + int(splitted_2[1]) * 60
        
        lis = line.findAll("li")
        output += time + "\n"
        for li in lis:
            output += li.getText() + "\n"
        output += "\n"    

    await context.bot.editMessageText(chat_id=update.effective_chat.id, text=output, message_id=messageID, reply_markup=markup)
    
async def QueryHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global messageID
    messageID = update.effective_message.id
    
    global markup
    markup = InlineKeyboardMarkup([[button1], [button2]])
        
    callback_data = update.callback_query.data
    
    if(callback_data == "today"):
        await Today(update, context)
    elif(callback_data == "tomorrow"):
        await Tomorrow(update, context)
        
async def GetLastUpdateID(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messageID = update.effective_message.id
    

if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler('start', Start)
    today_handler = CommandHandler('today', Today)
    tomorrow_handler = CommandHandler('tomorrow', Tomorrow)
    
    application.add_handler(CallbackQueryHandler(QueryHandler))
        
    application.add_handler(start_handler)
    application.add_handler(today_handler)
    application.add_handler(tomorrow_handler)
    
    application.run_polling()
    
