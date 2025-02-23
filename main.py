import logging
import requests
import json
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Разрешаем вложенные циклы событий (например, в Jupyter Notebook)
nest_asyncio.apply()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Словарь для хранения истории диалога для каждого чата
conversation_histories = {}

# Ваши токены и URL API
TELEGRAM_BOT_TOKEN = '7561462930:AAESoDgJdy5wik0gLNAlGE4ktazuVBk8ttY'
OPENROUTER_API_KEY = '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'
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я Эщкере-бот, который запоминает диалог и может анализировать изображения. Задавайте вопросы!")
    conversation_histories[update.effective_chat.id] = []

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Инициализируем историю диалога для этого чата, если её ещё нет
    if chat_id not in conversation_histories:
        conversation_histories[chat_id] = []

    # Формирование сообщения пользователя для API
    if update.message.photo:
        # Если в сообщении содержится изображение, выбираем самое большое
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_url = file.file_path
        caption = update.message.caption if update.message.caption else "Что изображено на этом фото?"
        user_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": caption},
                {"type": "image_url", "image_url": {"url": file_url}}
            ]
        }
    else:
        user_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": update.message.text}
            ]
        }

    # Добавляем сообщение пользователя в историю диалога
    conversation_histories[chat_id].append(user_message)

    # Подготавливаем данные для запроса к OpenRouter API
    payload = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": conversation_histories[chat_id]
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            result = response.json()
            reply_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            if not reply_text:
                reply_text = "Извините, я не смог обработать ваш запрос."
        else:
            reply_text = f"Ошибка API: {response.status_code}"
    except Exception as e:
        logger.error(f"Ошибка при запросе к API: {e}")
        reply_text = "Произошла ошибка при обращении к API."

    # Сохраняем ответ бота в истории диалога
    bot_message = {
        "role": "assistant",
        "content": [
            {"type": "text", "text": reply_text}
        ]
    }
    conversation_histories[chat_id].append(bot_message)

    # Отправляем ответ пользователю
    await update.message.reply_text(reply_text)

async def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Добавляем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))

    # Запуск бота
    await application.run_polling()
if __name__ == '__main__':
    asyncio.run(main())
