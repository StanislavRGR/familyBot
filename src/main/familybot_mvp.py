#!/usr/bin/env python3
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем токен из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Ошибка: BOT_TOKEN не найден. Убедись, что он указан в .env")

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


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


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Все текстовые сообщения → проверка на упоминание
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_mention))

    logger.info("Бот запущен. Ожидаю сообщения...")
    app.run_polling()


if __name__ == "__main__":
    main()
