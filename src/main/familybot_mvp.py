#!/usr/bin/env python3
import logging
import os
import json
import random
from datetime import time
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
    JobQueue
)

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем токен и чат_id из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # ID чата, куда бот будет слать пожелания

if not TOKEN:
    raise ValueError("Ошибка: BOT_TOKEN не найден. Убедись, что он указан в .env")

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Функция загрузки пожеланий из wishes.json
def load_wishes():
    with open("../../wishes.json", "r", encoding="utf-8") as f:
        return json.load(f)


# Функция для отправки ежедневного пожелания
async def send_daily_wish(context: ContextTypes.DEFAULT_TYPE):
    wishes = load_wishes()
    wish = random.choice(wishes)
    chat_id = CHAT_ID
    if not chat_id:
        logger.warning("CHAT_ID не задан. Сообщение не отправлено.")
        return
    await context.bot.send_message(chat_id=chat_id, text=f"🌞 Доброе утро!\n\n{wish}")


# Обычный echo при упоминании
async def echo_mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    entities = update.message.entities or []
    bot_mentioned = any(
        e.type == "mention"
        and update.message.text[e.offset:e.offset + e.length] == f"@{context.bot.username}"
        for e in entities
    )

    if bot_mentioned:
        user = update.message.from_user
        reply_text = f"@{user.username or user.first_name}, ты написал:\n\n{update.message.text}"

        logger.info(
            f"Сообщение от {user.full_name} (@{user.username}): {update.message.text}"
        )
        logger.info(f"Ответ бота: {reply_text}")

        await update.message.reply_text(reply_text)


# Команда /getchatid
async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"🆔 ID этого чата: `{chat_id}`", parse_mode="Markdown")
    logger.info(f"Пользователь запросил chat_id: {chat_id}")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Добавляем хендлеры
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_mention))
    app.add_handler(CommandHandler("getchatid", get_chat_id))

    # Настраиваем ежедневную задачу в 09:00 по Москве
    job_queue: JobQueue = app.job_queue
    job_queue.run_daily(
        send_daily_wish,
        time=time(hour=9, minute=0, tzinfo=ZoneInfo("Europe/Moscow"))
    )

    # ⚡ Тестовая задача: одно пожелание через 10 секунд после запуска
    job_queue.run_once(send_daily_wish, when=10)

    logger.info("Бот запущен. Ожидаю сообщения и готов к ежедневным пожеланиям...")
    app.run_polling()


if __name__ == "__main__":
    main()
