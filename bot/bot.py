import asyncio
import os
import httpx

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Set BOT_TOKEN in env or .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Простое in-memory хранилище состояний ---
user_ids = {}              # telegram_id -> student_id
pending_subject = {}       # telegram_id -> выбранный предмет (None = ждём выбор предмета)
pending_registration = {}  # telegram_id -> True если ждем ФИ для регистрации

SUBJECTS = ["Математика", "Русский язык", "Физика", "Информатика", "Химия", "Литература", "Биология"]


@dp.message(Command("start"))
async def cmd_start(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/register"), KeyboardButton(text="/enter_scores")],
            [KeyboardButton(text="/view_scores")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Привет! Я помогу вести твои баллы ЕГЭ.\n"
        "Команды:\n"
        "/register - зарегистрировать студента\n"
        "/enter_scores - ввести баллы\n"
        "/view_scores - посмотреть результаты\n"
        "/cancel - отменить текущее действие",
        reply_markup=kb
    )


# ----- Регистрация -----
@dp.message(Command("register"))
async def cmd_register(message: Message):
    user_id = message.from_user.id
    pending_registration[user_id] = True
    # убираем клавиатуру, чтобы пользователь просто ввёл "Иван Иванов"
    await message.answer("Отправь своё имя и фамилию через пробел (например: Иван Иванов). Для отмены нажми /cancel.",
                         reply_markup=ReplyKeyboardMarkup(keyboard=[[]], resize_keyboard=True))


@dp.message(F.text.regexp(r"^\S+\s+\S+$"))
async def handle_name(message: Message):
    user_id = message.from_user.id
    # Обработка только если пользователь действительно в состоянии регистрации
    if user_id not in pending_registration:
        return

    first_name, last_name = message.text.split(maxsplit=1)
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_URL}/students/", json={
            "first_name": first_name,
            "last_name": last_name
        }, timeout=10)
    if resp.status_code == 201:
        student = resp.json()
        user_ids[user_id] = student["id"]
        await message.answer(f"Зарегистрирован как: {student['first_name']} {student['last_name']}")
    else:
        await message.answer(f"Ошибка при регистрации: {resp.status_code} {resp.text}")

    # Снимаем флаг ожидания регистрации
    pending_registration.pop(user_id, None)


# ----- Ввод баллов -----
@dp.message(Command("enter_scores"))
async def cmd_enter_scores(message: Message):
    user_id = message.from_user.id
    if user_id not in user_ids:
        await message.answer("Сначала зарегистрируйся через /register")
        return

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=s)] for s in SUBJECTS] + [[KeyboardButton(text="/cancel")]],
        resize_keyboard=True
    )
    # помечаем: пользователь в режиме выбора предмета
    pending_subject[user_id] = None
    await message.answer("Выбери предмет (кнопкой):", reply_markup=kb)


@dp.message(F.text.in_(SUBJECTS))
async def choose_subject(message: Message):
    user_id = message.from_user.id
    # действуем только если пользователь в режиме ввода баллов
    if user_id not in pending_subject:
        return

    # Зафиксировали предмет и попросили ввести балл
    pending_subject[user_id] = message.text
    await message.answer(f"Введи балл по предмету {message.text} (0-100). Для отмены нажми /cancel.",
                         reply_markup=ReplyKeyboardMarkup(
                             keyboard=[[KeyboardButton(text="/cancel")]],
                             resize_keyboard=True
                         ))


@dp.message(F.text & ~F.text.startswith("/"))
async def handle_score(message: Message):
    user_id = message.from_user.id
    # действуем только если пользователь действительно в режиме ввода баллов
    if user_id not in pending_subject:
        return

    subject = pending_subject.get(user_id)
    # Если предмет ещё не выбран — игнорируем (пользователь может писать что-то другое)
    if subject is None:
        await message.answer("Пожалуйста, выбери предмет кнопкой из списка или нажми /cancel.")
        return

    # Парсим и валидируем балл
    try:
        score = int(message.text.strip())
        if not (0 <= score <= 100):
            raise ValueError
    except ValueError:
        await message.answer("Введи корректный числовой балл от 0 до 100.")
        return

    # Сохраняем через API
    student_id = user_ids.get(user_id)
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_URL}/students/{student_id}/scores/", json={
            "subject": subject,
            "score": score
        }, timeout=10)

    if resp.status_code in (200, 201):
        await message.answer(f"Сохранил: {subject} → {score}")
    else:
        await message.answer(f"Ошибка при сохранении: {resp.status_code} {resp.text}")

    # выходим из режима ввода баллов
    pending_subject.pop(user_id, None)


# ----- Просмотр баллов -----
@dp.message(Command("view_scores"))
async def cmd_view_scores(message: Message):
    user_id = message.from_user.id
    if user_id not in user_ids:
        await message.answer("Сначала зарегистрируйся через /register")
        return

    student_id = user_ids[user_id]
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_URL}/students/{student_id}/scores/", timeout=10)

    if resp.status_code == 200:
        scores = resp.json()
        if scores:
            text = "\n".join(f"{s['subject']}: {s['score']}" for s in scores)
            await message.answer(f"Твои баллы:\n{text}")
        else:
            await message.answer("У тебя пока нет сохранённых баллов.")
    else:
        await message.answer(f"Ошибка при получении баллов: {resp.status_code} {resp.text}")


# ----- Отмена -----
@dp.message(Command("cancel"))
async def cmd_cancel(message: Message):
    user_id = message.from_user.id
    pending_subject.pop(user_id, None)
    pending_registration.pop(user_id, None)
    await message.answer("Действие отменено. Возвращаю главное меню.",
                         reply_markup=ReplyKeyboardMarkup(
                             keyboard=[
                                 [KeyboardButton(text="/register"), KeyboardButton(text="/enter_scores")],
                                 [KeyboardButton(text="/view_scores")]
                             ],
                             resize_keyboard=True
                         ))


# ----- main -----
async def main():
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
