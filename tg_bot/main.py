import asyncio
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import sqlite3
import random, datetime
from dbgetset import *
from dotenv import load_dotenv
import os

load_dotenv()
print("Started")
TOKEN = os.getenv("token")
ADMIN_ID = os.getenv("admin_id")
print("Started2")
router = Router()
dp = Dispatcher()

dp.include_router(router)

bot = Bot(TOKEN, parse_mode="HTML")

class Form(StatesGroup):
    code = State()


@router.message(Command(commands=["start"]))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    if message.chat.type != "private":
        return
    elif str(message.chat.id) == str(ADMIN_ID):
        buttons = [[KeyboardButton(text="Проверить тесты")], [KeyboardButton(text="Показать код для добавления ученика")]]
        kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
        await message.answer("Этот бот предназначен для получения кода ученикам.\nВы авторизованы как учитель, воспользуйтесь меню!", reply_markup=kb)
    else:
        try:
            res = get_user(user_id=message.chat.id)
        except Exception as e:
            print(f"Error: {e}")
        if res != None:  
            get_code = [[KeyboardButton(text="Получить код на 45 мин")]]
            keyb = ReplyKeyboardMarkup(keyboard=get_code, resize_keyboard=True)
            await message.answer("Этот бот предназначен для получения кода, который понадобится при отправке заданий в нашем плагине\nИспользуй меню для получения кода",reply_markup=keyb)
        else:
            await message.answer("Вы не записаны в базе данных, пожалуйста пришлите код выданный учителем!")
            await state.set_state(Form.code)

@router.message(Form.code)
async def get_code(message: Message, state: FSMContext):
    code = message.text
    with sqlite3.connect("/tgbot/database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM codes WHERE code = ?", (code, ))
        res = cursor.fetchone()
    if res:
        await message.answer("Код был введен верно, ожидайте пока учитель настроит ваш аккаунт!")
        user_teach = res[0]
        classs = ["9А","9Б","9В","9К","9М"]
        buttons = []
        for i in classs:
            buttons.append([InlineKeyboardButton(text=i, callback_data="class:"+i+f":{str(message.chat.id)}")])
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await bot.send_message(user_teach, "Ученик ввел ваш код, пожалуйста выберите класс ученика", reply_markup=kb)
        await state.clear()
    else:
        await message.answer("Код был введен неверно, пожалуйста попробуйте еще раз!")

@router.callback_query(F.data.contains("class"))
async def set_class(call: CallbackQuery):
    i, classs, user_id = call.data.split(":")
    names = ["Куклин Антон","Лепский Кирилл","Китаева Анна"]
    buttons = []
    for i in names:
        buttons.append([InlineKeyboardButton(text=i, callback_data=f"lk:{classs}:{user_id}:{i}")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id, "Выберите имя для аккаунта ученика!",reply_markup=kb)

@router.callback_query(F.data.contains("lk"))
async def set_all(call: CallbackQuery):
    i, classs, user_id, name = call.data.split(":")
    insert_name(user_id, classs, name)
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(user_id, "Вы были успешно добавлены в систему!")
    await call.answer("Ученик был успешно добавлен в систему!")

@router.message()
async def show_qr(message: Message):
    if message.text == "Показать код для добавления ученика" or message.text == "Проверить тесты":
        if str(message.chat.id) == ADMIN_ID:
            if message.text == "Показать код для добавления ученика":
                code = random.randint(11111,999999)
                with sqlite3.connect("/tgbot/database.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT OR REPLACE INTO codes VALUES (?, ?)", (ADMIN_ID, str(code), ))
                    conn.commit()
                await message.answer(f"Код для добавления ученика: {code}")
            elif message.text == "Проверить тесты":
                buttons = ["9А","9Б","9В","9Г","9Д","9К"]
                kb=[]
                for button in buttons:
                    kb.append([InlineKeyboardButton(text=button, callback_data="check_"+button)])
                key = InlineKeyboardMarkup(inline_keyboard=kb)
                await bot.send_message(chat_id=message.chat.id, text="Выберите класс для просмотра", reply_markup=key)
        else:
            await message.answer("У вас нету доступа к этой команде!")
        
    elif message.text == "Получить код на 45 мин" or message.text == "Получить новый код":
        res = select_one_from_classes(str(message.chat.id))
        if res != None:
            code = random.randint(1000,100000)
            print(insert_code_res(str(message.chat.id), str(code), str(datetime.datetime.now() + datetime.timedelta(minutes=45))))
            button = [[KeyboardButton(text="Получить новый код")]]
            kb = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)
            await message.answer(
                f"Этот код будет работать 45 минут: *{code}* после чего он перестанет работать\. \(Новый можно запросить кнопкой ниже\)", parse_mode="MarkdownV2", reply_markup=kb)

@router.callback_query(F.data.contains("check_"))
async def check_class(call: CallbackQuery):
    classs = call.data.split("_")[1]
    tests = ["1", "2","3","4"]
    kb = []
    for test in tests:
        kb.append([InlineKeyboardButton(text=test, callback_data="test_"+test+"_"+classs)])
    key = InlineKeyboardMarkup(inline_keyboard=kb)
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text="Выберите номер теста для проверки", reply_markup=key)

@router.callback_query(F.data.contains("test_"))
async def check_test(call: CallbackQuery):
    i, test, classs = call.data.split("_")
    current_day = datetime.datetime.now().day
    kb = []
    for day in range(current_day-4, current_day+1):
        kb.append([InlineKeyboardButton(text=str(day), callback_data="date_"+str(day)+"_"+test+"_"+classs)])
    key = InlineKeyboardMarkup(inline_keyboard=kb)
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text="Выберите день для проверки", reply_markup=key)

@router.callback_query(F.data.contains("date_") or F.data.contains("repeat_"))
async def check_test(call: CallbackQuery):
    i, date, test, classs = call.data.split("_")
    print(classs)
    users = select_all_from_classes_class(classs)
    res = ''
    print(users)
    print(type(users))
    i = 0
    for user in users:
        if i == 0:
            res = user["user_id"]
        else:
            res += "OR "+user["user_id"]
    print(res)
    data = select_all_from_tests(res)
    datan = []
    if data != None:
        for user in data:
            print(datetime.datetime.strptime(user["last_date"], "%Y-%m-%d %H:%M:%S.%f").day)
            print(date)
            if datetime.datetime.strptime(user["last_date"], "%Y-%m-%d %H:%M:%S.%f").day == int(date):
                print(user["test"])
                print(test)
                if user["test"] == test:
                    print(user["test"])
                    print(test)
                    datan.append(user)
        kb = []
        print(datan)
        for user in datan:
            print(user)
            kb.append([InlineKeyboardButton(text=user["name"]+" кол.во "+user["count"],callback_data="user_"+str(date)+"_"+test+"_"+classs+"_"+user["user_id"])])
        kb.append([InlineKeyboardButton(text="Назад", callback_data="menu")])
        key = InlineKeyboardMarkup(inline_keyboard=kb)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text="Выберите ученика для просмотра попыток",reply_markup=key)
    else:
        kb = []
        kb.append([InlineKeyboardButton(text="Назад", callback_data="menu")])
        kb.append([InlineKeyboardButton(text="Обновить", callback_data="repeat_"+date+"_"+test+"_"+classs)])
        key1 = InlineKeyboardMarkup(inline_keyboard=kb)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text="Проделанных тестов пока что нету",reply_markup=key1)

@router.callback_query(F.data.contains("menu"))
async def menu(call: CallbackQuery):
    buttons = ["9А","9Б","9В","9Г","9Д","9К"]
    kb=[]
    for button in buttons:
        kb.append([InlineKeyboardButton(text=button, callback_data="check_"+button)])
    key = InlineKeyboardMarkup(inline_keyboard=kb)
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text="Выберите класс для просмотра", reply_markup=key)


@router.callback_query(F.data.contains("user_"))
async def check_user(call: CallbackQuery):
    i, date, test, classs, user_id = call.data.split("_")
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        users = select_all_from_classes_class(classs)
        res = ''
        i = 0
        for user in users:
            if i == 0:
                res = user["user_id"]
            else:
                res += "OR "+user[0]
        data = select_all_from_tests(res)
        datan = []
        for user in data:
            if datetime.datetime.strptime(user["last_date"], "%Y-%m-%d %H:%M:%S.%f").day == int(date):
                if user["test"] == test:
                    if user["user_id"] == user_id:
                        datan.append(user)
    kb = [[InlineKeyboardButton(text="Назад",callback_data="date_"+date+"_"+test+"_"+classs)]]
    key = InlineKeyboardMarkup(inline_keyboard=kb)
    pop = datan[0]['result'].replace(":","\n")
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=f"Имя: {datan[0]['name']}\nПопытки:\n{pop}\nКоличество попыток: {datan[0]['count']}\nВремя последней попытки: {str(datetime.datetime.strptime(datan[0]['last_date'], '%Y-%m-%d %H:%M:%S.%f').hour) + ':' + str(datetime.datetime.strptime(datan[0]['last_date'], '%Y-%m-%d %H:%M:%S.%f').minute) + ':' + str(datetime.datetime.strptime(datan[0]['last_date'], '%Y-%m-%d %H:%M:%S.%f').second)}",reply_markup=key)

async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())