import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

# Импортируем обновленные функции базы данных
from database import init_db, add_user, get_all_users, get_user_language, set_user_language

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- СЛОВАРЬ ТЕКСТОВ (МУЛЬТИЯЗЫЧНОСТЬ) ---
TEXTS = {
    "ukr": {
        "welcome": "Привіт, {name}! 👋\n\nЯ — бот-візитка та твій особистий менеджер. Тут ти можеш переглянути мої роботи, дізнатися ціни та відразу залишити заявку на розробку власного бота! 🚀\n\nОбери потрібний розділ у меню нижче 👇",
        "menu_title": "Головне меню 👇\nОбери потрібний розділ:",
        "btn_portfolio": "📁 Портфоліо",
        "btn_price": "💰 Прайс / Послуги",
        "btn_about": "🧑‍💻 Про мене",
        "btn_order": "🚀 Замовити бота",
        "btn_back": "🔙 Назад",
        "btn_cancel": "❌ Скасувати",
        "btn_lang": "🌐 Змінити мову",
        "portfolio_text": "📁 Моє Портфоліо та Стек:\n\nЯ спеціалізуюся на створенні асинхронних рішень для бізнесу та автоматизації.\n\n🛠 Мій стек технологій:\n• Python\n• Aiogram 3\n• SQLite3 / PostgreSQL\n• Git / GitHub\n\nНижче ти можеш переглянути вихідний код моїх розробок:",
        "price_text": "💰 Прайс-лист на розробку ботів:\n\n1. Бот-візитка / Меню / Інформаційний — від 50$\n2. Комерційний бот з Базою Даних — від 100$\n3. Складні системи / Інтеграції — індивідуально\n\n⏱ Терміни: від 3 до 7 днів.\n⚙️ Підтримка: Безкоштовне виправлення багів протягом 14 днів!",
        "about_text": "🧑‍💻 Про мене:\n\nПривіт! Я — Python-розробник, який створює ефективних Telegram-ботів під ключ.\n\nЧому обирають мене?\n• Пишу чистий та модульний код, який легко масштабувати.\n• Використовую сучасну бібліотеку Aiogram 3, тому боти працюють миттєво.\n• Завжди на зв'язку з клієнтом та допомагаю з розгортанням бота на сервер.",
        "order_start": "🚀 Чудово! Опиши, будь ласка, свою ідею або технічне завдання (ТЗ) одним повідомленням.\n\nЩо повинен робити бот? Для якого бізнесу?",
        "order_cancel": "❌ Замовлення скасовано. Повертаємось у головне меню.",
        "order_success": "✅ Дякую! Твоя заявка успішно надіслана розробнику.\n\nЯ зв'яжуся з тобою найближчим часом! 🤝"
    },
    "rus": {
        "welcome": "Привет, {name}! 👋\n\nЯ — бот-визитка и твой личный менеджер. Здесь ты можешь посмотреть мои работы, узнать цены и сразу оставить заявку на разработку собственного бота! 🚀\n\nВыбери нужный раздел в меню ниже 👇",
        "menu_title": "Главное меню 👇\nВыбери нужный раздел:",
        "btn_portfolio": "📁 Портфолио",
        "btn_price": "💰 Прайс / Услуги",
        "btn_about": "🧑‍💻 Обо мне",
        "btn_order": "🚀 Заказать бота",
        "btn_back": "🔙 Назад",
        "btn_cancel": "❌ Отменить",
        "btn_lang": "🌐 Сменить язык",
        "portfolio_text": "📁 Мое Портфолио и Стек:\n\nЯ специализируюсь на создании асинхронных решений для бизнеса и автоматизации.\n\n🛠 Мой стек технологий:\n• Python\n• Aiogram 3\n• SQLite3 / PostgreSQL\n• Git / GitHub\n\nНиже ты можешь посмотреть исходный код моих разработок:",
        "price_text": "💰 Прайс-лист на разработку ботов:\n\n1. Бот-визитка / Меню / Информационный — от 50$\n2. Коммерческий бот с Базой Данных — от 100$\n3. Сложные системы / Интеграции — индивидуально\n\n⏱ Сроки: от 3 до 7 дней.\n⚙️ Поддержка: Бесплатное исправление багов в течение 14 дней!",
        "about_text": "🧑‍💻 Обо мне:\n\nПривет! Я — Python-разработчик, который создает эффективных Telegram-ботов под ключ.\n\nПочему выбирают меня?\n• Пишу чистый и модульный код, который легко масштабировать.\n• Использую современную библиотеку Aiogram 3, поэтому боты работают мгновенно.\n• Всегда на связи с клиентом и помогаю с развертыванием бота на сервер.",
        "order_start": "🚀 Отлично! Опиши, пожалуйста, свою идею или техническое задание (ТЗ) одним сообщением.\n\nЧто должен делать бот? Для какого бизнеса?",
        "order_cancel": "❌ Заказ отменен. Возвращаемся в главное меню.",
        "order_success": "✅ Спасибо! Твоя заявка успешно отправлена разработчику.\n\nЯ свяжусь с тобой в ближайшее время! 🤝"
    },
    "eng": {
        "welcome": "Hello, {name}! 👋\n\nI'm a portfolio bot and your personal manager. Here you can check my projects, find out prices, and leave a request for your own bot development! 🚀\n\nChoose the section below 👇",
        "menu_title": "Main Menu 👇\nChoose a section:",
        "btn_portfolio": "📁 Portfolio",
        "btn_price": "💰 Price / Services",
        "btn_about": "🧑‍💻 About Me",
        "btn_order": "🚀 Order a Bot",
        "btn_back": "🔙 Back",
        "btn_cancel": "❌ Cancel",
        "btn_lang": "🌐 Сменить язык",
        "portfolio_text": "📁 My Portfolio & Stack:\n\nI specialize in building asynchronous solutions for business and automation.\n\n🛠 My tech stack:\n• Python\n• Aiogram 3\n• SQLite3 / PostgreSQL\n• Git / GitHub\n\nBelow you can view the source code of my projects:",
        "price_text": "💰 Price list for bot development:\n\n1. Promo Bot / Menu / Informational — from $50\n2. Commercial Bot with Database — from $100\n3. Complex Systems / Integrations — custom price\n\n⏱ Terms: 3 to 7 days.\n⚙️ Support: Free bug fixing for 14 days after launch!",
        "about_text": "🧑‍💻 About Me:\n\nHi! I'm a Python developer crafting high-performance Telegram bots from scratch.\n\nWhy choose me?\n• I write clean, modular code that is easy to scale.\n• I use the modern Aiogram 3 library, ensuring instant response times.\n• Always in touch with the client and ready to help with server deployment.",
        "order_start": "🚀 Great! Please describe your idea or tech specifications (TS) in a single message.\n\nWhat should the bot do? What kind of business is it for?",
        "order_cancel": "❌ Order cancelled. Returning to main menu.",
        "order_success": "✅ Thank you! Your request has been successfully sent to the developer.\n\nI will contact you shortly! 🤝"
    }
}


# --- НАСТРОЙКА FSM ---
class OrderStates(StatesGroup):
    waiting_for_tz = State()


class AdminStates(StatesGroup):
    waiting_for_broadcast_text = State()


# --- КЛАВИАТУРЫ ---
def get_language_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🇺🇦 Українська", callback_data="set_lang_ukr"))
    builder.add(types.InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_rus"))
    builder.add(types.InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_eng"))
    builder.adjust(1)
    return builder.as_markup()


def get_main_keyboard(lang):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=TEXTS[lang]["btn_portfolio"], callback_data="portfolio"))
    builder.add(types.InlineKeyboardButton(text=TEXTS[lang]["btn_price"], callback_data="price"))
    builder.add(types.InlineKeyboardButton(text=TEXTS[lang]["btn_about"], callback_data="about"))
    builder.add(types.InlineKeyboardButton(text=TEXTS[lang]["btn_order"], callback_data="order"))
    # Добавляем кнопку смены языка на всю ширину (1 кнопка в ряду)
    builder.add(types.InlineKeyboardButton(text=TEXTS[lang]["btn_lang"], callback_data="change_language_route"))

    builder.adjust(2, 2, 1) # Первые два ряда по 2 кнопки, последний ряд — 1 кнопка
    return builder.as_markup()


def get_cancel_keyboard(lang):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=TEXTS[lang]["btn_cancel"], callback_data="cancel_order"))
    return builder.as_markup()


def get_portfolio_keyboard(lang):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🌐 GitHub", url="https://github.com/MaX45165/portfolio-bot"))
    builder.add(types.InlineKeyboardButton(text=TEXTS[lang]["btn_back"], callback_data="back_to_menu"))
    builder.adjust(1)
    return builder.as_markup()


def get_back_keyboard(lang):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=TEXTS[lang]["btn_back"], callback_data="back_to_menu"))
    return builder.as_markup()


def get_admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"))
    builder.add(types.InlineKeyboardButton(text="📢 Сделать рассылку", callback_data="admin_broadcast"))
    builder.adjust(1)
    return builder.as_markup()


# --- КЛИЕНТСКАЯ ЧАСТЬ ---
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    username = message.from_user.username if message.from_user.username else "NoUsername"
    add_user(user_id=message.from_user.id, username=username)

    if message.from_user.id == ADMIN_ID:
        admin_welcome = (
            f"Привет, Босс! 😎👋\n\n"
            f"Системы работают стабильно, мультиязычность подключена.\n\n"
            f"Ты зашел как администратор. Вот твоя панель управления 👇"
        )
        await message.answer(text=admin_welcome, reply_markup=get_admin_keyboard())
        return

    # При старте сначала всегда предлагаем выбрать язык
    await message.answer(text="Оберіть мову / Выберите язык / Choose a language 🌐",
                         reply_markup=get_language_keyboard())


# Обработка выбора языка
@dp.callback_query(lambda c: c.data.startswith("set_lang_"))
async def process_language_choice(callback: types.CallbackQuery):
    lang = callback.data.split("_")[2]  # Получаем 'ukr', 'rus' или 'eng'
    set_user_language(callback.from_user.id, lang)

    # Приветствие на выбранном языке
    welcome = TEXTS[lang]["welcome"].format(name=callback.from_user.full_name)
    await callback.message.edit_text(text=welcome, reply_markup=get_main_keyboard(lang))
    await callback.answer()


@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        await callback.message.edit_text(text="👑 Панель администратора:", reply_markup=get_admin_keyboard())
        await callback.answer()
        return

    lang = get_user_language(callback.from_user.id)
    await callback.message.edit_text(text=TEXTS[lang]["menu_title"], reply_markup=get_main_keyboard(lang))
    await callback.answer()


@dp.callback_query(lambda c: c.data in ["portfolio", "price", "about"])
async def handle_info_buttons(callback: types.CallbackQuery):
    lang = get_user_language(callback.from_user.id)

    if callback.data == "portfolio":
        await callback.message.edit_text(text=TEXTS[lang]["portfolio_text"], reply_markup=get_portfolio_keyboard(lang))
    elif callback.data == "price":
        await callback.message.edit_text(text=TEXTS[lang]["price_text"], reply_markup=get_back_keyboard(lang))
    elif callback.data == "about":
        await callback.message.edit_text(text=TEXTS[lang]["about_text"], reply_markup=get_back_keyboard(lang))

    await callback.answer()


@dp.callback_query(lambda c: c.data == "order")
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_language(callback.from_user.id)
    await callback.message.answer(text=TEXTS[lang]["order_start"], reply_markup=get_cancel_keyboard(lang))
    await state.set_state(OrderStates.waiting_for_tz)
    await callback.answer()


@dp.callback_query(lambda c: c.data == "cancel_order")
async def cancel_order(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    if callback.from_user.id == ADMIN_ID:
        await callback.message.answer("❌ Рассылка отменена.", reply_markup=get_admin_keyboard())
    else:
        lang = get_user_language(callback.from_user.id)
        await callback.message.answer(text=TEXTS[lang]["order_cancel"], reply_markup=get_main_keyboard(lang))
    await callback.answer()

@dp.callback_query(lambda c: c.data == "change_language_route")
async def change_language_route(callback: types.CallbackQuery):
    # Просто сносим старое меню и выводим выбор из трех языков, как при старте
    await callback.message.edit_text(
        text="Оберіть мову / Выберите язык / Choose a language 🌐",
        reply_markup=get_language_keyboard()
    )
    await callback.answer()

@dp.message(OrderStates.waiting_for_tz)
async def process_tz(message: types.Message, state: FSMContext):
    client_tz = message.text
    client_username = f"@{message.from_user.username}" if message.from_user.username else "No Username"
    lang = get_user_language(message.from_user.id)

    admin_notification = (
        f"🚨 НОВАЯ ЗАЯВКА НА БОТА!\n\n"
        f"👤 Клиент: {message.from_user.full_name}\n"
        f"🔗 Юзернейм: {client_username}\n"
        f"🌐 Язык клиента: {lang.upper()}\n\n"
        f"📝 ТЗ:\n{client_tz}"
    )

    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_notification)
        await message.answer(text=TEXTS[lang]["order_success"], reply_markup=get_main_keyboard(lang))
    except Exception as e:
        await message.answer("⚠️ Error.")
        print(f"Ошибка: {e}")

    await state.clear()


# --- АДМИНСКАЯ ЧАСТЬ ---
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("👑 Приветствую, Бос! Это секретная админ-панель.", reply_markup=get_admin_keyboard())


@dp.callback_query(lambda c: c.data in ["admin_stats", "admin_broadcast"])
async def handle_admin_buttons(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return

    if callback.data == "admin_stats":
        users = get_all_users()
        count = len(users)
        await callback.message.answer(f"📊 Статистика:\nВсего пользователей в базе: {count}")
    elif callback.data == "admin_broadcast":
        await callback.message.answer(
            "📢 Отправь сообщение (текст/фото), которое получат ВСЕ пользователи (независимо от их языка):",
            reply_markup=get_cancel_keyboard("rus"))
        await state.set_state(AdminStates.waiting_for_broadcast_text)
    await callback.answer()


@dp.message(AdminStates.waiting_for_broadcast_text)
async def process_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    users = get_all_users()
    success_count = 0

    for user_id in users:
        if user_id == ADMIN_ID:
            continue
        try:
            await message.copy_to(chat_id=user_id)
            success_count += 1
        except Exception:
            pass

    await message.answer(f"✅ Рассылка завершена!\nСообщение получили: {success_count} пользователей.")
    await state.clear()


async def main():
    init_db()
    add_user(user_id=ADMIN_ID, username="Admin")
    print("Мультиязычный бот успешно запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())