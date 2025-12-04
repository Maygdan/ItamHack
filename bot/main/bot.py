import os
import django
import sys

# Add the project directory to the sys.path
project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(project_dir, 'A_back'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from mini.models import LoginCode  # type: ignore[import]
from django.contrib.auth.models import User  # type: ignore[import]
from bot_settings import TOKEN, FRONTEND_URL
import telebot
from random import choices
import string
from django.utils import timezone
from datetime import timedelta

bot = telebot.TeleBot(TOKEN)

# Генерация 8-символьного кода
def generate_code():
    characters = string.ascii_letters + string.digits
    return ''.join(choices(characters, k=8))

# Команда /help
@bot.message_handler(commands=['help'])
def help_command(message):
    text = (
        "💡 <b>Добро пожаловать в регистрацию!</b>\n\n"
        "Этот бот предназначен для входа на платформу <b>DateHack</b>.\n"
        "Скопируйте код или перейдите по сгенерированной ссылке для входа."
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML')

# Команда /start - может принимать параметр для автоматического входа
@bot.message_handler(commands=['start'])
def start_command(message):
    # Проверяем, есть ли параметр после /start
    command_parts = message.text.split()
    start_param = command_parts[1] if len(command_parts) > 1 else None

    if start_param == 'login':
        # Автоматически выполняем логику входа - всегда генерируем новый код (если сессия кончилась)
        start_login_command(message)
    else:
        help_command(message)

# Функция для автоматического входа через start (всегда новый код, если возможно)
def start_login_command(message):
    telegram_id = str(message.from_user.id)
    user_name = message.from_user.username or message.from_user.first_name

    # Проверяем, есть ли у пользователя действительная сессия (менее 24 часов с последнего входа)
    try:
        user = User.objects.get(username=telegram_id)
        if user.last_login and (timezone.now() - user.last_login) < timedelta(days=1):
            # У пользователя есть активная сессия
            remaining_hours = int(((user.last_login + timedelta(days=1)) - timezone.now()).total_seconds() / 3600)
            text = (
                f"👋 Приветствую, <b>{user_name}</b>!\n\n"
                f"🔒 <b>У вас уже есть активная сессия</b>\n\n"
                f"⏳ <i>Сессия истечёт через {remaining_hours} часов</i>\n\n"
                f"Вы можете войти на платформу обычным способом или подождать истечения сессии."
            )
            bot.send_message(message.chat.id, text, parse_mode='HTML')
            return
    except User.DoesNotExist:
        # Пользователь ещё не зарегистрирован, можно продолжить
        pass

    # Генерируем новый код (игнорируем существующие)
    code = generate_code()
    expires_at = timezone.now() + timedelta(minutes=5)
    LoginCode.objects.create(code=code, telegram_id=telegram_id, expires_at=expires_at)

    frontend_url = FRONTEND_URL
    link = f"{frontend_url}/telegram-login?code={code}"

    text = (
        f"👋 Приветствую, <b>{user_name}</b>!\n\n"
        f"✅ <b>Код для входа:</b> <code>{code}</code>\n\n"
        f"<a href='{link}'>🔗 Войти на платформу</a>\n\n"
        f"⏳ <i>Истекает через 5 минут</i>"
    )

    bot.send_message(message.chat.id, text, parse_mode='HTML')

# Команда /login - может показать существующий код
@bot.message_handler(commands=['login'])
def login_command(message):
    telegram_id = str(message.from_user.id)
    user_name = message.from_user.username or message.from_user.first_name

    # Проверяем, есть ли у пользователя действительная сессия (менее 24 часов с последнего входа)
    try:
        user = User.objects.get(username=telegram_id)
        if user.last_login and (timezone.now() - user.last_login) < timedelta(days=1):
            # У пользователя есть активная сессия
            remaining_hours = int(((user.last_login + timedelta(days=1)) - timezone.now()).total_seconds() / 3600)
            text = (
                f"👋 Приветствую, <b>{user_name}</b>!\n\n"
                f"🔒 <b>У вас уже есть активная сессия</b>\n\n"
                f"⏳ <i>Сессия истечёт через {remaining_hours} часов</i>\n\n"
                f"Вы можете войти на платформу обычным способом или подождать истечения сессии."
            )
            bot.send_message(message.chat.id, text, parse_mode='HTML')
            return
    except User.DoesNotExist:
        # Пользователь ещё не зарегистрирован, можно продолжить
        pass

    # Проверяем, есть ли у пользователя действительный неиспользованный код
    existing_code = LoginCode.objects.filter(
        telegram_id=telegram_id,
        used=False,
        expires_at__gt=timezone.now()
    ).first()

    if existing_code:
        # Есть действительный код - показываем его (без кнопки)
        remaining_time = int((existing_code.expires_at - timezone.now()).total_seconds() / 60)
        text = (
            f"👋 Приветствую, <b>{user_name}</b>!\n\n"
            f"✅ <b>У вас уже есть действующий код:</b> <code>{existing_code.code}</code>\n\n"
            f"⏳ <i>Истекает через {remaining_time} минут</i>\n\n"
            f"Используйте этот код для входа на платформу."
        )
        bot.send_message(message.chat.id, text, parse_mode='HTML')
    else:
        # Генерируем новый код и показываем кнопку
        code = generate_code()
        expires_at = timezone.now() + timedelta(minutes=5)
        LoginCode.objects.create(code=code, telegram_id=telegram_id, expires_at=expires_at)

        frontend_url = FRONTEND_URL
        link = f"{frontend_url}/telegram-login?code={code}"

        text = (
            f"👋 Приветствую, <b>{user_name}</b>!\n\n"
            f"✅ <b>Код для входа:</b> <code>{code}</code>\n\n"
            f"<a href='{link}'>🔗 Войти на платформу</a>\n\n"
            f"⏳ <i>Истекает через 5 минут</i>"
        )

        bot.send_message(message.chat.id, text, parse_mode='HTML')

bot.polling()
